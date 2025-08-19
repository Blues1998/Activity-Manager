"""
Tracker Manager — orchestrates all trackers (keyboard, mouse, apps, idle).
Provides unified APIs for the GUI and storage.
"""

from activity_manager.trackers.keyboard_tracker import KeyboardTracker
from activity_manager.trackers.mouse_tracker import MouseTracker
from activity_manager.trackers.app_tracker import AppTracker
from activity_manager.trackers.idle_tracker import IdleTracker
from activity_manager.storage.storage_manager import StorageManager


class TrackerManager:
    def __init__(self):
        # Storage (logs everything to file by default)
        self.storage = StorageManager(mode="file", path="logs/activity.log")

        # Initialize trackers
        self.keyboard = KeyboardTracker()
        self.mouse = MouseTracker()
        self.app = AppTracker()
        self.idle = IdleTracker()

        # Start background trackers
        self.keyboard.start()
        self.mouse.start()
        self.app.start()
        self.idle.start()

    def get_dashboard_data(self):
        return {
            "last_keys": self.keyboard.get_last_keys(),
            "mouse_stats": self.mouse.get_stats(),
            "active_app": self.app.get_active_app(),
            "recent_apps": self.app.get_recent_apps(),
            "idle_time": self.idle.get_idle_time(),
        }

    def get_last_keys(self):
        return self.keyboard.get_last_keys()

    def get_active_app(self):
        return self.app.get_active_app()

    def get_stats(self):
        """Return a dictionary of tracked stats."""
        return {
            "keys": self.keyboard.count,
            "mouse_moves": self.mouse.moves,
            "idle_time": self.idle.get_idle_time(),
            "active_app": self.app.get_active_app()
        }

    def close(self):
        """Gracefully close storage backend"""
        self.storage.close()
