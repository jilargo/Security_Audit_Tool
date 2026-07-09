import os
from pathlib import Path


def get_powershell_history():

    history_entries = []

    users_folder = Path("C:/Users")

    for user in users_folder.iterdir():

        history_file = (
            user /
            "AppData/Roaming/Microsoft/Windows/PowerShell/PSReadLine/ConsoleHost_history.txt"
        )

        if history_file.exists():

            try:
                with open(history_file, "r", encoding="utf-8", errors="ignore") as f:

                    commands = [line.strip() for line in f if line.strip()]

                history_entries.append({
                    "User": user.name,
                    "HistoryFile": str(history_file),
                    "Commands": commands
                })

            except Exception:
                pass

    return history_entries


def print_history(limit=40):

    histories = get_powershell_history()

    if not histories:
        print("No PowerShell history found.")
        return
    for history in histories:
        
        commands = history["Commands"]

        print("=" * 70)
        print(f"User         : {history['User']}")
        print(f"History File : {history['HistoryFile']}")
        print(f"Total Commands: {len(commands)}")
        print(f"Showing Last : {min(limit, len(commands))} Commands")
        print("=" * 70)

        # Display only the last `limit` commands
        for index, command in enumerate(commands[-limit:], start=1):
            print(f"{index:2}. {command}")


