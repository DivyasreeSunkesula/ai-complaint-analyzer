# AI Complaint Analyzer

**AI Complaint Analyzer** is a cloud-native application that leverages **Google Generative AI (Gemini)** to classify, prioritize, summarize, and suggest actions for citizen complaints. It provides an automated, scalable solution for municipal departments, police, and emergency services.

## Features

- Submit complaints via **API** or **web UI**  
- **AI classification** of complaints into categories such as (Theft, Accident, Power, Medical, Unknown)  
- **Priority detection**: Critical, High, Medium, Low  
- **Automatic summarization** and suggested action  
- **Firestore database** to store complaints and AI results  
- **Dashboard** with:
  - Paginated, searchable complaint table  
  - Category and priority **pie charts**  
  - CSV export  
  - Complaint statistics
- **Health endpoint** for monitoring  
- Scalable deployment on **Google Cloud Run**  
- Elasticity testing with **Locust**

## Architecture

![Architecture Diagram](docs/architecture.png)

**Components**:

1. **Frontend**: User input and result display  
2. **FastAPI backend**: Receives complaints and manages API endpoints  
3. **Google Gemini AI**: Performs classification, prioritization, summarization, and action suggestions  
4. **Firestore**: Stores complaints and AI results  
5. **Cloud Run**: Scalable deployment of backend  
6. **Dashboard**: Visualization of statistics and trends  

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/ai-complaint-analyzer.git
cd ai-complaint-analyzer
```

2. **Create virtual environment and install dependencies**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. **Set environment variables**
```bash
export GEMINI_API_KEY="your_google_generative_ai_key"
export PORT=8080
```

4. **Run the application locally**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

5. Open the **UI:** http://0.0.0.0:8080

6. Open **Swagger docs:** http://0.0.0.0:8080/docs

## **API Endpoints**
**1. Submit Complaint**
- Endpoint: /submit
- Method: POST
- **Description:** Submits a citizen complaint for AI analysis. The AI classifies the complaint, assigns a priority, summarizes it, and suggests an action.
- **Request Body (JSON):**
```bash
{
  "complaint": "Power outage in my area for 3 hours"
}

```
**Response (JSON):**
```bash
{
  "doc_id": "abc123",
  "category": "Power",
  "priority": "Medium",
  "summary": "Citizen reports: Power outage in my area for 3 hours",
  "suggested_action": "Notify electricity department",
  "status": "New",
  "created_at": "2025-11-24T12:00:00Z"
}
```
**2. List Complaints**
- Endpoint: /complaints
- Method: GET
- **Description:** Returns a paginated, searchable list of complaints. Supports filtering by status and priority..
- **Query Parameters:**
-  `q`: search query
- `status`: filter by status
-  `priority`: filter by priority
-  `page, page_size`: pagination
- `sort_by, sort_dir`: sorting

**3. Update Status Endpoint**
- Endpoint: /update_status
- Method: POST
- **Description:** Updates the status of a complaint.
- **Request Body:**
```bash
  {
  "doc_id": "abc123",
  "status": "In-Progress"
  }
```
**4. Update Priority Endpoint**
- Endpoint: /update_priority
- Method: POST
- **Description:** Updates the priority of a complaint.
- **Request Body:**
```bash
  {
  "doc_id": "abc123",
  "priority": "Critical"
  }
```

**5. Update Category Endpoint**
- Endpoint: /update_category
- Method: POST
- **Description:** Updates the category of a complaint.
- **Request Body:**
```bash
  {
  "doc_id": "abc123",
  "category": "Accident"
  }
```
**6. Delete Complaint Endpoint**
- Endpoint: /delete_complaint
- Method: POST
- **Description:** Deletes a complaint.
- **Request Body:**
```bash
  {
 "doc_id": "abc123"
  }
```

**7. Export CSV**
- Endpoint: /export
- Method: GET
- Optional Query Parameters: status, priority

**8. Statistics**
- Endpoint: /stats
- Method: GET
Returns complaint counts, category distribution, priority distribution, and trends.

**9. Health Check**
- Endpoint: /health
- Method: GET
- Response: { "status": "ok" }

**Dashboard**

- Table: Paginated, searchable, sortable

- Charts: Pie charts for category and priority distributions

- CSV Export: Download filtered complaints

Screenshot Example: docs/dashboard.png

**AI Metrics**

- Metrics are evaluated using Precision, Recall, and F1-score.

- Use `evaluate_ai_metrics.py`:
```bash
python evaluate_ai_metrics.py
```
- Sample output
```bash
=== CATEGORY METRICS ===
Theft: Precision=1.00, Recall=0.67, F1=0.80
Accident: Precision=1.00, Recall=1.00, F1=1.00
Power: Precision=0.00, Recall=0.00, F1=0.00
Medical: Precision=0.67, Recall=1.00, F1=0.80
Unknown: Precision=1.00, Recall=1.00, F1=1.00

=== PRIORITY METRICS ===
Critical: Precision=1.00, Recall=1.00, F1=1.00
High: Precision=1.00, Recall=1.00, F1=1.00
Medium: Precision=1.00, Recall=1.00, F1=1.00
Low: Precision=1.00, Recall=1.00, F1=1.00

=== OVERALL AVERAGE ===
Category - Precision=0.96, Recall=0.96, F1=0.96
Priority - Precision=1.00, Recall=1.00, F1=1.00
```
Realistic metrics depend on diverse, representative test datasets.  
**Load & Elasticity Testing**
- Tool: Locust
- Simulate multiple users submitting complaints concurrently
- Validate Cloud Run scaling behavior
- Obaserve loud Run metrics at: https://console.cloud.google.com/run/detail/europe-west1/ai-complaint-analyzer/observability/metrics?orgonly=true&project=ai-complaint-analyzer&supportedpurview=organizationId
    
**Future Enhancements**
- Real-time notifications for critical complaints
- Multi-language support for citizen complaints
- Advanced trend predictions using AI
- Role-based dashboard with admin, officer and citizen views
  
**References**  
[Google Cloud Run Documentation](https://cloud.google.com/run/docs)  
[FastAPI Documentation](https://fastapi.tiangolo.com/)  
[Google Generative AI](https://developers.generativeai.google/)


