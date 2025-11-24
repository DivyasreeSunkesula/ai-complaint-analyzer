# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from agent import add_complaint, get_all_complaints, update_complaint_status
import os, re, json

# Gemini AI 
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

app = FastAPI(title="AI Complaint Analyzer")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure Gemini if available
if GEMINI_AVAILABLE:
    gem_key = os.getenv("GEMINI_API_KEY")
    if gem_key:
        genai.configure(api_key=gem_key)
        model = genai.GenerativeModel("models/gemini-2.5-flash")
    else:
        GEMINI_AVAILABLE = False

# Keyword-based fallback maps
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

def classify_fallback(complaint_text):
    text_lower = complaint_text.lower()
    # Determine category
    category = "Unknown"
    for cat, keywords in KEYWORD_CATEGORY_MAP.items():
        if any(k in text_lower for k in keywords):
            category = cat
            break
    # Determine priority
    priority = "Medium"
    for p, keywords in PRIORITY_KEYWORDS.items():
        if any(k in text_lower for k in keywords):
            priority = p
            break
    # Suggested action
    suggested_action = CATEGORY_ACTION_MAP.get(category, "Manual review")
    # Build result
    return {
        "category": category,
        "priority": priority,
        "summary": f"Citizen reports: {complaint_text}",
        "suggested_action": suggested_action
    }

@app.get("/", response_class=HTMLResponse)
def home():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/submit")
async def submit_complaint(request: Request):
    data = await request.json()
    complaint_text = data.get("complaint", "")

    if not complaint_text:
        return JSONResponse({"error": "Complaint text is required"}, status_code=400)

    # Gemini AI call
    if GEMINI_AVAILABLE:
        print("Using Gemini AI")
        prompt = f"""
        You are an AI assistant that classifies citizen complaints.
        Return ONLY a JSON object with keys:
        category, priority, summary, suggested_action
        Complaint: "{complaint_text}"
        """
        try:
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
        # Fallback if Gemini not available
        ai_result = classify_fallback(complaint_text)

    ai_result["status"] = "New"
    doc_id = add_complaint(ai_result)
    ai_result["doc_id"] = doc_id
    return JSONResponse(ai_result)

@app.get("/complaints")
def all_complaints():
    return JSONResponse(get_all_complaints())

@app.post("/update_status")
async def update_status(request: Request):
    data = await request.json()
    doc_id = data.get("doc_id")
    new_status = data.get("status")
    update_complaint_status(doc_id, new_status)
    return JSONResponse({"success": True})

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ai-complaint-analyzer-agent"}


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8080))  # Use PORT from environment
    uvicorn.run("main:app", host="0.0.0.0", port=port)
