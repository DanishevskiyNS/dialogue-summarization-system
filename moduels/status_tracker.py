import redis
import json
import os
from typing import Optional, Dict

class StatusTracker:
    def __init__(self):
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.redis_client = redis.from_url(redis_url)
        self.status_key_prefix = "task_status:"
        self.valid_statuses = [
            "uploaded",
            "preprocessed",
            "transcription_done", 
            "diarization_done",
            "summarization_done",
            "formatting_done",
            "completed",
            "failed"
        ]

    def set_status(self, task_id: str, status: str, details: Optional[Dict] = None) -> None:
        if status not in self.valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of: {self.valid_statuses}")
            
        status_data = {
            "status": status,
            "details": details or {},
            "pipeline_progress": {
                "preprocessed": status == "preprocessed",
                "transcription_done": status == "transcription_done",
                "diarization_done": status == "diarization_done", 
                "summarization_done": status == "summarization_done",
                "formatting_done": status == "formatting_done"
            }
        }
        self.redis_client.set(
            f"{self.status_key_prefix}{task_id}",
            json.dumps(status_data),
            ex=86400  # Expire after 24 hours
        )

    def get_status(self, task_id: str) -> Optional[Dict]:
        status_data = self.redis_client.get(f"{self.status_key_prefix}{task_id}")
        if status_data:
            return json.loads(status_data)
        return None

# Initialize status tracker
status_tracker = StatusTracker() 