# db.py
import os
from google.cloud import firestore


# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account.json"

# Initialize Firestore client
db = firestore.Client(project="ai-complaint-analyzer")

def add_complaint(complaint_data):
    """
    Add a new complaint to the 'complaints' collection.
    complaint_data: dict with keys like category, priority, summary, suggested_action, status
    """
    try:
        doc_ref = db.collection("complaints").document()  # Auto-generated ID
        doc_ref.set(complaint_data)
        return {"success": True, "id": doc_ref.id}
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_complaint_status(doc_id, status):
    """
    Update the status of an existing complaint
    """
    try:
        doc_ref = db.collection("complaints").document(doc_id)
        doc_ref.update({"status": status})
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_all_complaints():
    """
    Fetch all complaints
    """
    try:
        complaints = []
        docs = db.collection("complaints").stream()
        for doc in docs:
            complaint = doc.to_dict()
            complaint["id"] = doc.id
            complaints.append(complaint)
        return complaints
    except Exception as e:
        return {"success": False, "error": str(e)}
