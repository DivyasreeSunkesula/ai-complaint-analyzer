# agent.py
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import io
import csv

# Initialize Firebase app (expects service-account.json present)
if not firebase_admin._apps:
    cred = credentials.Certificate("service-account.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
complaints_col = db.collection("complaints")


def add_complaint(complaint_data: dict):
    """Add complaint to Firestore and return doc_id"""
    # Ensure created_at in ISO format with Z
    complaint_data = dict(complaint_data)  # copy
    complaint_data.setdefault("created_at", datetime.utcnow().isoformat() + "Z")
    # default field
    complaint_data.setdefault("status", "New")
    doc_ref = complaints_col.add(complaint_data)
    return doc_ref[1].id


def get_all_complaints():
    """Return all complaints from Firestore as list of dicts with doc_id"""
    docs = complaints_col.stream()
    results = []
    for d in docs:
        item = d.to_dict() or {}
        item["doc_id"] = d.id
        # normalize fields
        item.setdefault("category", "Unknown")
        item.setdefault("priority", "Medium")
        item.setdefault("status", "New")
        item.setdefault("created_at", "")
        item.setdefault("summary", "")
        item.setdefault("suggested_action", "")
        results.append(item)
    return results


def update_complaint_status(doc_id: str, status: str):
    """Update complaint status by doc_id"""
    complaints_col.document(doc_id).update({"status": status})


def update_complaint_priority(doc_id: str, priority: str):
    """Update complaint priority by doc_id"""
    complaints_col.document(doc_id).update({"priority": priority})


def update_complaint_category(doc_id: str, category: str):
    complaints_col.document(doc_id).update({"category": category})


def delete_complaint(doc_id: str):
    complaints_col.document(doc_id).delete()


def export_complaints_csv(filters: dict = None):
    """
    filters: dict with optional exact-match keys (status, priority, category)
    Returns CSV text as string.
    """
    q = complaints_col
    # apply simple equality filters
    if filters:
        for k, v in filters.items():
            if v:
                q = q.where(k, "==", v)
    docs = q.stream()

    output = io.StringIO()
    writer = csv.writer(output)
    header = ["doc_id", "category", "priority", "status", "summary", "suggested_action", "created_at"]
    writer.writerow(header)
    for d in docs:
        item = d.to_dict() or {}
        writer.writerow([
            d.id,
            item.get("category", ""),
            item.get("priority", ""),
            item.get("status", ""),
            item.get("summary", ""),
            item.get("suggested_action", ""),
            item.get("created_at", ""),
        ])
    return output.getvalue()


def compute_stats():
    """
    Returns aggregation stats:
    { "by_category": {cat: count, ...}, "by_priority": {priority: count, ...}, "total": n }
    """
    docs = complaints_col.stream()
    by_category = {}
    by_priority = {}
    total = 0
    for d in docs:
        total += 1
        item = d.to_dict() or {}
        cat = item.get("category", "Unknown")
        pr = item.get("priority", "Medium")
        by_category[cat] = by_category.get(cat, 0) + 1
        by_priority[pr] = by_priority.get(pr, 0) + 1
    return {"by_category": by_category, "by_priority": by_priority, "total": total}
