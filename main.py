"""
Security Audit Tool - application entry point.

Run with:  python main.py
"""

import sys
from pathlib import Path

# Make sure the project packages are importable regardless of the working directory
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from collectors.antivirus_info_collector import get_antivirus_info
from collectors.event_logs_collector import get_system_events
from collectors.firewall_status_collector import get_firewall_status
from collectors.installed_apps_collector import get_registry_value
from collectors.network_collector import get_network_connections
from collectors.powershell_history_collector import get_powershell_history
from collectors.process_collector import get_running_processes
from collectors.scheduled_task_collector import get_scheduled_tasks
from collectors.start_up_collectors import get_registry_startup_programs
from collectors.system_info_collector import get_system_info
from collectors.usb_history_collector import get_usb_history
from collectors.user_acounts_audit import get_local_users

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():

    # function call from imported modules

    # get_antivirus_info()
    # get_system_events()
    # get_firewall_status()
    # get_registry_value()
    # get_network_connections()
    # get_powershell_history()
    # get_running_processes()
    # get_scheduled_tasks()
    # get_registry_startup_programs()
    # get_system_info()
    # get_usb_history()
    # get_local_users()

    app = QApplication(sys.argv)
    app.setApplicationName("Security Audit Tool")
    app.setOrganizationName("Security Audit Tool")
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
