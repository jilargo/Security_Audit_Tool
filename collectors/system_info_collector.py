import platform
import socket
import psutil

def get_system_info():
    return {
        "Computer Name": socket.gethostname(),
        "Operating System": platform.system(),
        "OS Version": platform.version(),
        "Processor": platform.processor(),
        "CPU Cores": psutil.cpu_count(),
        "RAM (GB)": round(psutil.virtual_memory().total / (1024**3), 2)
    }