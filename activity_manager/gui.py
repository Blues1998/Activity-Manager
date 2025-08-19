"""
Graphical User Interface for Activity Manager.
Built with ttkbootstrap (modern Tkinter styling).
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from activity_manager.tracker_manager import TrackerManager


class ActivityManagerApp:
    def __init__(self):
        self.root = ttk.Window(themename="cosmo")
        self.root.title("Activity Manager")
        self.root.geometry("900x600")

        # Tracker Manager (handles all trackers)
        self.manager = TrackerManager()

        # Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Dashboard tab
        self.dashboard = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard, text="Dashboard")

        self.active_app_label = ttk.Label(self.dashboard, text="Active App: -", font=("Segoe UI", 12))
        self.active_app_label.pack(pady=10)

        self.recent_apps_label = ttk.Label(self.dashboard, text="Recent Apps: -", font=("Segoe UI", 12))
        self.recent_apps_label.pack(pady=10)

        self.last_keys_label = ttk.Label(self.dashboard, text="Last Keys: -", font=("Segoe UI", 12))
        self.last_keys_label.pack(pady=10)

        self.stats_label = ttk.Label(self.dashboard, text="Stats: -", font=("Segoe UI", 12))
        self.stats_label.pack(pady=10)

        self.idle_time_label = ttk.Label(self.dashboard, text="Idle Time: -", font=("Segoe UI", 12))
        self.idle_time_label.pack(pady=10)

        # Settings tab
        self.settings = ttk.Frame(self.notebook)
        self.notebook.add(self.settings, text="Settings")

        self.file_path_label = ttk.Label(self.settings, text="Log File Location: logs/keystrokes.log")
        self.file_path_label.pack(pady=10)

        # Polling update
        self.update_dashboard()

    def update_dashboard(self):
        data = self.manager.get_dashboard_data()

        # Active app
        self.active_app_label.config(text=f"Active App: {data['active_app']}")

        # Recent apps
        recent_apps = ", ".join(data['recent_apps'][:5]) if data['recent_apps'] else "-"
        self.recent_apps_label.config(text=f"Recent Apps: {recent_apps}")

        # Last keys
        self.last_keys_label.config(text=f"Last Keys: {data['last_keys']}")

        # Mouse stats
        mouse_stats = data['mouse_stats']
        self.stats_label.config(
            text=f"Mouse — Clicks: {mouse_stats['Clicks']} | Moves: {mouse_stats['Moves']} | Scrolls: {mouse_stats['Scrolls']}"
        )

        # Idle time
        self.idle_time_label.config(text=f"Idle Time: {data['idle_time']}s")

        # Schedule next update
        self.root.after(1000, self.update_dashboard)

    def run(self):
        """Run the Tkinter main loop."""
        self.root.mainloop()
