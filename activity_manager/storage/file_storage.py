import os
import json
from datetime import datetime


class FileStorage:
    def __init__(self, path="logs/activity.log"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.file = open(path, "a", encoding="utf-8")

    def log_event(self, event_type: str, details: dict):
        timestamp = datetime.now().isoformat()
        log_entry = {"time": timestamp, "type": event_type, "details": details}
        self.file.write(json.dumps(log_entry) + "\n")
        self.file.flush()

    def close(self):
        self.file.close()
