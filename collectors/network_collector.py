import psutil

def get_network_connections():
    connections = []

    for conn in psutil.net_connections(kind="inet"):
        try:
            process_name = None
            if conn.pid:
                process_name = psutil.Process(conn.pid).name()
            connection = {
                "LocalAddress": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                "RemoteAddress": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                "Status": conn.status,
                "PID": conn.pid,
                "ProcessName": process_name
            }

            connections.append(connection)

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            continue

    return connections

def print_network_connections():

    connections = get_network_connections()

    print(f"\nFound {len(connections)} network connections.\n")

    for index, connection in enumerate(connections, start=1):

        print("=" * 60)
        print(f"Connection #{index}")

        for key, value in connection.items():
            print(f"{key}: {value}")


