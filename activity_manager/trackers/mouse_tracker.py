# activity_manager/trackers/mouse_tracker.py

"""
Mouse Tracker — captures clicks, movement, and scrolls on macOS using Quartz.
Logs are aggregated for mouse moves (to avoid spam), but clicks/scrolls are logged immediately.

Requires:
- System Settings → Privacy & Security → Accessibility → allow your terminal/IDE
"""

import threading
import Quartz
import datetime
import json
import os

# ✅ Explicitly import CF run-loop symbols
from CoreFoundation import (
    CFMachPortCreateRunLoopSource,
    CFRunLoopGetCurrent,
    CFRunLoopAddSource,
    CFRunLoopRun,
    kCFRunLoopCommonModes,
)


class MouseTracker:
    """Background mouse listener using a CGEvent tap + CFRunLoop."""

    def __init__(self, log_file="logs/mouse.log", flush_interval=5):
        self.clicks = 0
        self.moves = 0
        self.scrolls = 0

        self._running = False
        self._thread = None

        # Logging
        self.log_file = log_file
        self.flush_interval = flush_interval
        self._last_flush = datetime.datetime.now()

        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    # ---- Logging ----------------------------------------------------------
    def _log(self, data: dict):
        """Append a JSON record to the log file."""
        with open(self.log_file, "a") as f:
            f.write(json.dumps(data) + "\n")

    def _flush_moves(self):
        """Write aggregated move stats and reset counter."""
        if self.moves > 0:
            record = {
                "ts": datetime.datetime.now().isoformat(),
                "event": "mouse_moves",
                "count": self.moves,
            }
            self._log(record)
            self.moves = 0

    # ---- CGEvent callback -------------------------------------------------
    def _callback(self, proxy, event_type, event, refcon):
        ts = datetime.datetime.now().isoformat()

        if event_type in (Quartz.kCGEventLeftMouseDown,
                          Quartz.kCGEventRightMouseDown,
                          Quartz.kCGEventOtherMouseDown):
            self.clicks += 1
            self._log({"ts": ts, "event": "click"})
        elif event_type in (Quartz.kCGEventMouseMoved,
                            Quartz.kCGEventLeftMouseDragged,
                            Quartz.kCGEventRightMouseDragged,
                            Quartz.kCGEventOtherMouseDragged):
            self.moves += 1
        elif event_type == Quartz.kCGEventScrollWheel:
            self.scrolls += 1
            self._log({"ts": ts, "event": "scroll"})

        # Periodically flush moves
        now = datetime.datetime.now()
        if (now - self._last_flush).total_seconds() >= self.flush_interval:
            self._flush_moves()
            self._last_flush = now

        return event

    # ---- Thread target: create tap and run loop ---------------------------
    def _run(self):
        event_mask = (
            (1 << Quartz.kCGEventLeftMouseDown)
            | (1 << Quartz.kCGEventRightMouseDown)
            | (1 << Quartz.kCGEventOtherMouseDown)
            | (1 << Quartz.kCGEventMouseMoved)
            | (1 << Quartz.kCGEventLeftMouseDragged)
            | (1 << Quartz.kCGEventRightMouseDragged)
            | (1 << Quartz.kCGEventOtherMouseDragged)
            | (1 << Quartz.kCGEventScrollWheel)
        )

        tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap,
            Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionDefault,
            event_mask,
            self._callback,
            None,
        )

        if not tap:
            print("[MouseTracker] ERROR: Failed to create event tap. "
                  "Check Accessibility permissions.")
            return

        run_loop_source = CFMachPortCreateRunLoopSource(None, tap, 0)
        loop = CFRunLoopGetCurrent()
        CFRunLoopAddSource(loop, run_loop_source, kCFRunLoopCommonModes)

        # Enable and run
        Quartz.CGEventTapEnable(tap, True)
        CFRunLoopRun()

    # ---- Public API -------------------------------------------------------
    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print("[MouseTracker] Started.")

    def stop(self):
        self._running = False
        self._flush_moves()  # flush any remaining moves
        print("[MouseTracker] Stopped.")

    def get_stats(self):
        return {
            "Clicks": self.clicks,
            "Moves": self.moves,
            "Scrolls": self.scrolls,
        }
