# activity_manager/trackers/application_tracker.py

import threading
import time
from AppKit import NSWorkspace


class AppTracker:
    def __init__(self):
        self.running = False
        self.thread = None
        self.last_app = None
        self.recent_apps = []  # keep a small history

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            print("[ApplicationTracker] Started.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        print("[ApplicationTracker] Stopped.")

    def _run(self):
        while self.running:
            active_app = NSWorkspace.sharedWorkspace().frontmostApplication()
            app_name = active_app.localizedName()
            bundle_id = active_app.bundleIdentifier()

            if app_name != self.last_app:
                self.last_app = app_name
                self.recent_apps.insert(0, f"{app_name} ({bundle_id})")
                self.recent_apps = self.recent_apps[:5]  # keep only last 5
                print(f"[ApplicationTracker] Active app: {app_name} ({bundle_id})")

            time.sleep(1)  # check every second

    def get_active_app(self):
        return self.last_app if self.last_app else "Unknown"

    def get_recent_apps(self):
        return self.recent_apps
