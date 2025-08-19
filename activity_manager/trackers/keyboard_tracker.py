# activity_manager/trackers/keyboard_tracker.py

import threading
import datetime
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

# Basic mapping of macOS keycodes to readable keys (can be expanded)
KEY_MAP = {
    0: "A",
    1: "S",
    2: "D",
    3: "F",
    4: "H",
    5: "G",
    6: "Z",
    7: "X",
    8: "C",
    9: "V",
    11: "B",
    12: "Q",
    13: "W",
    14: "E",
    15: "R",
    16: "Y",
    17: "T",
    18: "1",
    19: "2",
    20: "3",
    21: "4",
    22: "6",
    23: "5",
    24: "=",
    25: "9",
    26: "7",
    27: "-",
    28: "8",
    29: "0",
    30: "]",
    31: "O",
    32: "U",
    33: "[",
    34: "I",
    35: "P",
    36: "Return",
    37: "L",
    38: "J",
    39: "'",
    40: "K",
    41: ";",
    42: "\\",
    43: ",",
    44: "/",
    45: "N",
    46: "M",
    47: ".",
    49: "Space",
    51: "Delete",
    53: "Escape",
    123: "Left",
    124: "Right",
    125: "Down",
    126: "Up",
}


class KeyboardTracker:
    def __init__(self, callback=None, buffer_size=10):
        """
        :param callback: function accepting (timestamp, key_code, event_type)
        """
        self.callback = callback
        self.running = False
        self.thread = None

        # keep last N keys
        self.last_keys = deque(maxlen=buffer_size)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            print("[KeyboardTracker] Started.")

    def stop(self):
        self.running = False
        print("[KeyboardTracker] Stopped.")

    def get_last_keys(self):
        """Return a list of recently pressed keys (human-readable if possible)."""
        return list(self.last_keys)

    def _run(self):
        def callback(proxy, type_, event, refcon):
            if type_ in (kCGEventKeyDown, kCGEventKeyUp):
                key_code = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
                ts = datetime.datetime.now()

                if type_ == kCGEventKeyDown:
                    key_str = KEY_MAP.get(key_code, f"[{key_code}]")  # fallback to raw number
                    self.last_keys.append(key_str)

                if self.callback:
                    self.callback(ts, key_code, type_)

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
            print("[KeyboardTracker] ERROR: Could not create event tap. Do you have accessibility permissions?")
            return

        run_loop_source = CF.CFMachPortCreateRunLoopSource(None, tap, 0)
        CF.CFRunLoopAddSource(
            CF.CFRunLoopGetCurrent(),
            run_loop_source,
            CF.kCFRunLoopDefaultMode,
        )

        CGEventTapEnable(tap, True)

        CF.CFRunLoopRun()
