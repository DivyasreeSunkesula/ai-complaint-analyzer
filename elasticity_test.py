import random
import uuid
from locust import HttpUser, task, between

class ComplaintAnalyzerUser(HttpUser):
    """
    Elasticity test user for your AI Complaint Analyzer FastAPI service.
    """

    wait_time = between(1, 2)  # Faster cycles to trigger scaling

    def on_start(self):
        """Set up user identity for test."""
        self.user_id = f"user_{uuid.uuid4()}"

    @task(4)
    def submit_complaint(self):
        """Send random citizen complaints to /submit."""
        sample_complaints = [
            "There is a power outage in my area for the past 3 hours.",
            "My bike was stolen near the railway station.",
            "A major accident happened on the main road, people are injured.",
            "There is a critical medical emergency in my neighborhood.",
            "Electric transformer burst, sparks everywhere.",
            "A robbery attempt happened in my apartment complex.",
        ]

        payload = {
            "complaint": random.choice(sample_complaints)
        }
