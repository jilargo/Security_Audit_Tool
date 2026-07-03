from collectors.system_info_collector import print_system_info
from collectors.event_logs_collector import print_event_logs
from collectors.installed_apps_collector import print_installed_apps
from collectors.process_collector import print_processes

def main():
     print_system_info()
     print_event_logs()
     print_installed_apps()
     print_processes()
     


if __name__ == "__main__":
     main()