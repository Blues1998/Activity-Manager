"""
Main entry point for Activity Manager application.
"""

from activity_manager.gui import ActivityManagerApp


def main():
    """Launch the Activity Manager application."""
    app = ActivityManagerApp()
    app.run()


if __name__ == "__main__":
    main()
