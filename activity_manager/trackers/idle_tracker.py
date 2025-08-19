"""
Idle Tracker — detects idle time using macOS Quartz APIs.
"""

import Quartz


class IdleTracker:
    def __init__(self):
        self.running = False

    def start(self):
        """Start the idle tracker (placeholder for consistency)."""
        self.running = True
        print("[IdleTracker] Started.")

    def stop(self):
        """Stop the idle tracker."""
        self.running = False
        print("[IdleTracker] Stopped.")

    def get_idle_time(self) -> int:
        """
        Returns idle time in seconds.
        Uses Quartz.CGEventSourceSecondsSinceLastEventType to query system idle time.
        """
        if not self.running:
            return 0

        idle = Quartz.CGEventSourceSecondsSinceLastEventType(
            Quartz.kCGEventSourceStateCombinedSessionState,
            Quartz.kCGAnyInputEventType
        )
        return int(idle)
