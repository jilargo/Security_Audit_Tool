import psutil
from datetime import datetime


def bytes_to_mb(value):
    return round(value / (1024 * 1024), 2)


def get_running_processes():

    processes = []

    for process in psutil.process_iter():

        try:

            info = process.as_dict(attrs=[
                "pid",
                "ppid",
                "name",
                "username",
                "exe",
                "status",
                "create_time",
                "memory_info",
                "num_threads"
            ])

            process_data = {

                "PID": info["pid"],

                "ParentPID": info["ppid"],

                "Name": info["name"],

                "Username": info["username"],

                "Executable": info["exe"],

                "Status": info["status"],

                "CPUPercent": process.cpu_percent(interval=0.1),

                "MemoryMB": bytes_to_mb(
                    info["memory_info"].rss
                ),

                "Threads": info["num_threads"],

                "StartTime": datetime.fromtimestamp(
                    info["create_time"]
                ).strftime("%Y-%m-%d %H:%M:%S")

            }

            processes.append(process_data)

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            continue

    return processes
def print_processes():

    processes = get_running_processes()

    print(f"\nRunning Processes: {len(processes)}\n")

    for process in processes:

        print("=" * 60)

        for key, value in process.items():
            print(f"{key}: {value}")

