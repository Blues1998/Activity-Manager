"""
Storage Manager — provides unified logging API.
Currently only file-based logging is supported.
"""

from activity_manager.storage.file_storage import FileStorage


class StorageManager:
    def __init__(self, mode="file", path="logs/activity.log"):
        if mode != "file":
            raise ValueError("Only 'file' mode supported right now.")
        self.backend = FileStorage(path)

    def log_event(self, event_type: str, details: dict):
        self.backend.log_event(event_type, details)

    def close(self):
        self.backend.close()
