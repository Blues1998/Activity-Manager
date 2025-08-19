# activity_manager/trackers/idle_tracker.py

import os
import json
import Quartz
import threading
import time
import datetime


class IdleTracker:
    def __init__(self, storage=None, interval=10, idle_threshold=60):
        """
        :param storage: optional storage backend (must implement .log_event)
        :param interval: how often (in seconds) to check idle time
        :param idle_threshold: how many seconds counts as "idle"
        """
        self.running = False
        self.thread = None
        self.storage = storage
        self.interval = interval
        self.idle_threshold = idle_threshold
        self._was_idle = False  # track state to avoid spamming

        os.makedirs("logs", exist_ok=True)
        self.log_file = "logs/idle.log"

    def start(self):
        """Start the idle tracker thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            print("[IdleTracker] Started.")

    def stop(self):
        """Stop the idle tracker."""
        self.running = False
        if self.thread:
            self.thread.join()
        print("[IdleTracker] Stopped.")

    def get_idle_time(self) -> int:
        """Return system idle time in seconds."""
        idle = Quartz.CGEventSourceSecondsSinceLastEventType(
            Quartz.kCGEventSourceStateCombinedSessionState,
            Quartz.kCGAnyInputEventType
        )
        return int(idle)

    def _run(self):
        """Background loop that periodically logs idle state."""
        while self.running:
            idle_seconds = self.get_idle_time()
            ts = datetime.datetime.now().isoformat()

            # If idle crosses threshold and wasn't already idle → log once
            if idle_seconds > self.idle_threshold and not self._was_idle:
                event = {"timestamp": ts, "idle_seconds": idle_seconds}

                # write to file
                with open(self.log_file, "a") as f:
                    f.write(json.dumps(event) + "\n")

                # optional storage
                if self.storage:
                    self.storage.log_event("idle", event)

                self._was_idle = True

            # If user became active again
            if idle_seconds <= self.idle_threshold and self._was_idle:
                self._was_idle = False

            time.sleep(self.interval)
