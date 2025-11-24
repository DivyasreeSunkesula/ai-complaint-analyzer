# main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict
import os, re, json, io
from datetime import datetime

from agent import (
    add_complaint,
    get_all_complaints,
    update_complaint_status,
    update_complaint_priority,
    update_complaint_category,
    delete_complaint,
    export_complaints_csv,
    compute_stats,
)

# Gemini AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

app = FastAPI(title="AI Complaint Analyzer")
app.mount("/static", StaticFiles(directory="static"), name="static")

if GEMINI_AVAILABLE:
    gem_key = os.getenv("GEMINI_API_KEY")
    if gem_key:
        genai.configure(api_key=gem_key)
        model = genai.GenerativeModel("models/gemini-2.5-flash")
    else:
        GEMINI_AVAILABLE = False

KEYWORD_CATEGORY_MAP = {
    "Theft": ["stolen", "snatched", "robbery", "theft", "bike missing", "chain snatching"],
    "Accident": ["accident", "injured", "crash", "fatal", "collision"],
    "Power": ["power outage", "transformer", "electricity", "load shedding", "electric"],
    "Medical": ["health", "injury", "hospital", "ambulance", "critical"],
}

CATEGORY_ACTION_MAP = {
    "Theft": "Advise citizen to file a police report and provide identifying details.",
    "Accident": "Dispatch emergency services immediately.",
    "Power": "Notify electricity department.",
    "Medical": "Call nearest hospital or ambulance.",
    "Unknown": "Manual review"
}

PRIORITY_KEYWORDS = {
    "Critical": ["critical", "life threat", "fatal", "injury"],
    "High": ["urgent", "emergency"],
}

# -------------------------------
# Pydantic Models for Swagger
# -------------------------------
class ComplaintRequest(BaseModel):
    complaint: str

class ComplaintUpdateStatus(BaseModel):
    doc_id: str
    status: str

class ComplaintUpdatePriority(BaseModel):
    doc_id: str
    priority: str

class ComplaintUpdateCategory(BaseModel):
    doc_id: str
    category: str

class ComplaintDeleteRequest(BaseModel):
    doc_id: str

class ComplaintResponse(BaseModel):
    doc_id: str
    category: str
    priority: str
    summary: str
    suggested_action: str
    status: str
    created_at: str

# -------------------------------
# Fallback classification
# -------------------------------
def classify_fallback(complaint_text: str) -> Dict:
    text_lower = complaint_text.lower()
    category = "Unknown"
    for cat, keywords in KEYWORD_CATEGORY_MAP.items():
        if any(k in text_lower for k in keywords):
            category = cat
            break
    priority = "Medium"
    for p, keywords in PRIORITY_KEYWORDS.items():
        if any(k in text_lower for k in keywords):
            priority = p
            break
    return {
        "category": category,
        "priority": priority,
        "summary": f"Citizen reports: {complaint_text}",
        "suggested_action": CATEGORY_ACTION_MAP.get(category, "Manual review"),
    }

# -------------------------------
# Endpoints
# -------------------------------
@app.get("/", response_class=HTMLResponse)
def home():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/submit", response_model=ComplaintResponse)
async def submit_complaint(data: ComplaintRequest):
    complaint_text = data.complaint
    if not complaint_text:
        raise HTTPException(status_code=400, detail="Complaint text required")

    if GEMINI_AVAILABLE:
        try:
            prompt = f"""
            You are an AI assistant that classifies citizen complaints.
            Return ONLY a JSON object with keys:
            category, priority, summary, suggested_action
            Complaint: "{complaint_text}"
            """
            ai_response = model.generate_content(prompt)
            ai_text = ai_response.text.strip()
            json_match = re.search(r"\{.*\}", ai_text, re.DOTALL)
            if json_match:
                ai_result = json.loads(json_match.group())
            else:
                ai_result = classify_fallback(complaint_text)
        except Exception:
            ai_result = classify_fallback(complaint_text)
    else:
        ai_result = classify_fallback(complaint_text)

    ai_result["status"] = "New"
    ai_result["created_at"] = datetime.utcnow().isoformat() + "Z"
    doc_id = add_complaint(ai_result)
    ai_result["doc_id"] = doc_id
    return ai_result


@app.get("/complaints")
def list_complaints(
    q: str = Query("", description="search query"),
    status: str = Query("", description="filter by status"),
    priority: str = Query("", description="filter by priority"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=500),
    sort_by: str = Query("created_at"),
    sort_dir: str = Query("desc", regex="^(asc|desc)$"),
):
    all_docs = get_all_complaints()

    def matches(item):
        if not q:
            return True
        ql = q.lower()
        return (
            ql in (item.get("doc_id", "").lower())
            or ql in (item.get("category", "").lower())
            or ql in (item.get("summary", "").lower())
            or ql in (item.get("status", "").lower())
            or ql in (item.get("priority", "").lower())
        )

    filtered = [d for d in all_docs if matches(d)]
    if status:
        filtered = [d for d in filtered if d.get("status", "").lower() == status.lower()]
    if priority:
        filtered = [d for d in filtered if d.get("priority", "").lower() == priority.lower()]

    reverse = sort_dir == "desc"
    try:
        filtered.sort(key=lambda x: x.get(sort_by, ""), reverse=reverse)
    except Exception:
        filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    items = filtered[start:end]

    return {"total": total, "page": page, "page_size": page_size, "items": items}


@app.post("/update_status")
async def update_status_endpoint(data: ComplaintUpdateStatus):
    update_complaint_status(data.doc_id, data.status)
    return {"success": True}


@app.post("/update_priority")
async def update_priority_endpoint(data: ComplaintUpdatePriority):
    update_complaint_priority(data.doc_id, data.priority)
    return {"success": True}


@app.post("/update_category")
async def update_category_endpoint(data: ComplaintUpdateCategory):
    update_complaint_category(data.doc_id, data.category)
    return {"success": True}


@app.post("/delete_complaint")
async def delete_complaint_endpoint(data: ComplaintDeleteRequest):
    delete_complaint(data.doc_id)
    return {"success": True}


@app.get("/export")
def export_csv(status: str = Query("", description="filter by status"), priority: str = Query("", description="filter by priority")):
    filters = {}
    if status:
        filters["status"] = status
    if priority:
        filters["priority"] = priority
    csv_text = export_complaints_csv(filters)
    return StreamingResponse(io.StringIO(csv_text), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=complaints.csv"})


@app.get("/stats")
def stats():
    return compute_stats()


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
