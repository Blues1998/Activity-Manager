"""
Mouse Tracker — captures clicks, movement, and scrolls on macOS using Quartz.
Tested with Python 3.13 + pyobjc on Apple Silicon.

Requires:
- System Settings → Privacy & Security → Accessibility → allow your terminal/IDE
"""

import threading
import Quartz

# ✅ Explicitly import CF run-loop symbols to avoid PyObjC lazy-load KeyError
from CoreFoundation import (
    CFMachPortCreateRunLoopSource,
    CFRunLoopGetCurrent,
    CFRunLoopAddSource,
    CFRunLoopRun,
    kCFRunLoopCommonModes,
)


class MouseTracker:
    """Background mouse listener using a CGEvent tap + CFRunLoop."""

    def __init__(self):
        self.clicks = 0
        self.moves = 0
        self.scrolls = 0
        self._running = False
        self._thread = None

    # ---- CGEvent callback -------------------------------------------------
    def _callback(self, proxy, event_type, event, refcon):
        if event_type in (Quartz.kCGEventLeftMouseDown, Quartz.kCGEventRightMouseDown,
                          Quartz.kCGEventOtherMouseDown):
            self.clicks += 1
        elif event_type in (Quartz.kCGEventMouseMoved,
                            Quartz.kCGEventLeftMouseDragged,
                            Quartz.kCGEventRightMouseDragged,
                            Quartz.kCGEventOtherMouseDragged):
            self.moves += 1
        elif event_type == Quartz.kCGEventScrollWheel:
            self.scrolls += 1
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

        # ⤵️ Use directly-imported CF* functions (works with PyObjC 10+)
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
        print("[MouseTracker] Stopped.")

    def get_stats(self):
        return {
            "Clicks": self.clicks,
            "Moves": self.moves,
            "Scrolls": self.scrolls,
        }
