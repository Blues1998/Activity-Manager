# activity_manager/trackers/keyboard_tracker.py

import os
import threading
import datetime
import time
from collections import deque
from Quartz.CoreGraphics import (
    CGEventTapCreate,
    CGEventTapEnable,
    CGEventGetIntegerValueField,
    kCGEventKeyDown,
    kCGEventKeyUp,
    kCGEventTapOptionDefault,
    kCGHeadInsertEventTap,
    kCGSessionEventTap,
    kCGKeyboardEventKeycode,
)
import CoreFoundation as CF
import json

KEY_MAP = {
    0: "a", 1: "s", 2: "d", 3: "f", 4: "h", 5: "g", 6: "z", 7: "x", 8: "c", 9: "v",
    11: "b", 12: "q", 13: "w", 14: "e", 15: "r", 16: "y", 17: "t", 18: "1", 19: "2",
    20: "3", 21: "4", 22: "6", 23: "5", 24: "=", 25: "9", 26: "7", 27: "-", 28: "8",
    29: "0", 30: "]", 31: "o", 32: "u", 33: "[", 34: "i", 35: "p", 36: "\n",  # Return
    37: "l", 38: "j", 39: "'", 40: "k", 41: ";", 42: "\\", 43: ",", 44: "/", 45: "n",
    46: "m", 47: ".", 49: " ",  # Space
    51: "[DEL]", 53: "[ESC]",
    123: "[LEFT]", 124: "[RIGHT]", 125: "[DOWN]", 126: "[UP]",
}


class KeyboardTracker:
    def __init__(self, storage=None, buffer_size=10, flush_interval=5):
        self.storage = storage
        self.running = False
        self.thread = None
        self.last_keys = deque(maxlen=buffer_size)
        self.text_buffer = ""  # human-readable typed text
        self.flush_interval = flush_interval
        self.last_flush = time.time()

        os.makedirs("logs", exist_ok=True)
        self.log_file = "logs/keyboard.log"
        self.summary_file = "logs/summary.log"

    def _append_to_summary(self, key_str):
        """Builds natural text and flushes periodically."""
        if key_str == "\n":  # Enter key
            self._flush(force=True)
        elif key_str == "[DEL]":
            self.text_buffer = self.text_buffer[:-1]
        elif len(key_str) == 1 or key_str == " ":
            self.text_buffer += key_str
        # Ignore arrows, escape, etc.

        # Periodic flush
        now = time.time()
        if now - self.last_flush > self.flush_interval:
            self._flush()

    def _flush(self, force=False):
        """Write buffer to file if non-empty."""
        if self.text_buffer.strip():
            with open(self.summary_file, "a") as f:
                f.write(self.text_buffer + ("\n" if force else " "))
            self.text_buffer = ""
        self.last_flush = time.time()

    def _log_event(self, key_str, ts):
        event = {"timestamp": ts, "key": key_str}

        # Raw JSON log
        with open(self.log_file, "a") as f:
            f.write(json.dumps(event) + "\n")

        # Update summary
        self._append_to_summary(key_str)

        # Optional storage
        if self.storage:
            self.storage.log_event("keyboard", event)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            print("[KeyboardTracker] Started.")

    def stop(self):
        self.running = False
        CF.CFRunLoopStop(CF.CFRunLoopGetCurrent())  # stop loop
        print("[KeyboardTracker] Stopped.")

    def get_last_keys(self):
        return list(self.last_keys)

    def _run(self):
        def callback(proxy, type_, event, refcon):
            if type_ == kCGEventKeyDown:
                key_code = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
                ts = datetime.datetime.now().isoformat()
                key_str = KEY_MAP.get(key_code, f"[{key_code}]")
                self.last_keys.append(key_str)
                self._log_event(key_str, ts)
            return event

        event_mask = (1 << kCGEventKeyDown) | (1 << kCGEventKeyUp)
        tap = CGEventTapCreate(
            kCGSessionEventTap,
            kCGHeadInsertEventTap,
            kCGEventTapOptionDefault,
            event_mask,
            callback,
            None,
        )

        if not tap:
            print("[KeyboardTracker] ERROR: Could not create event tap. "
                  "Do you have accessibility permissions?")
            return

        run_loop_source = CF.CFMachPortCreateRunLoopSource(None, tap, 0)
        CF.CFRunLoopAddSource(CF.CFRunLoopGetCurrent(), run_loop_source, CF.kCFRunLoopDefaultMode)
        CGEventTapEnable(tap, True)
        CF.CFRunLoopRun()
