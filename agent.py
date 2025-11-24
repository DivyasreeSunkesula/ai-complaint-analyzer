# agent.py
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("service-account.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
complaints_col = db.collection("complaints")

def add_complaint(complaint_data):
    """Add complaint to Firestore and return doc_id"""
    complaint_data["created_at"] = datetime.utcnow().isoformat()
    doc_ref = complaints_col.add(complaint_data)
    return doc_ref[1].id

def get_all_complaints():
    """Return all complaints from Firestore"""
    docs = complaints_col.stream()
    return [dict(doc.to_dict(), doc_id=doc.id) for doc in docs]

def update_complaint_status(doc_id, status):
    """Update complaint status by doc_id"""
    doc_ref = complaints_col.document(doc_id)
    doc_ref.update({"status": status})
