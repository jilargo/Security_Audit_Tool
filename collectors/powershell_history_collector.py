from pathlib import Path
from datetime import datetime
import os


SUSPICIOUS_KEYWORDS = [
    "invoke-expression",
    "iex ",
    "downloadstring",
    "invoke-webrequest",
    "net.webclient",
    "start-bitstransfer",
    "encodedcommand",
    "-enc ",
    "powershell -nop",
    "bypass",
    "mimikatz",
    "credential",
    "password",
    "sam",
    "lsass"
]


def check_suspicious_command(command):

    command_lower = command.lower()

    findings = []

    for keyword in SUSPICIOUS_KEYWORDS:

        if keyword in command_lower:
            findings.append(keyword)

    return ", ".join(findings) if findings else "None"


def get_powershell_history():

    history_entries = []

    users_folder = Path("C:/Users")

    audit_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    for user in users_folder.iterdir():

        # Skip invalid folders
        if not user.is_dir():
            continue


        possible_history_locations = [

            # Windows PowerShell 5.1
            user /
            "AppData/Roaming/Microsoft/Windows/PowerShell/PSReadLine/ConsoleHost_history.txt",

            # PowerShell 7+
            user /
            "AppData/Roaming/Microsoft/PowerShell/PSReadLine/ConsoleHost_history.txt"

        ]


        for history_file in possible_history_locations:


            if history_file.exists():

                try:

                    file_created = datetime.fromtimestamp(
                        history_file.stat().st_ctime
                    ).strftime("%Y-%m-%d %H:%M:%S")


                    file_modified = datetime.fromtimestamp(
                        history_file.stat().st_mtime
                    ).strftime("%Y-%m-%d %H:%M:%S")


                    with open(
                        history_file,
                        "r",
                        encoding="utf-8",
                        errors="ignore"
                    ) as f:


                        for index, line in enumerate(f, start=1):

                            command = line.strip()


                            if command:


                                history_entries.append({

                                    "User": user.name,

                                    "Command Number": index,

                                    "PowerShell Command": command,

                                    "Suspicious Activity":
                                        check_suspicious_command(command),

                                    "History File":
                                        str(history_file),

                                    "File Created":
                                        file_created,

                                    "File Modified":
                                        file_modified,

                                    "Audit Scan Date":
                                        audit_time
                                })


                except Exception as error:

                    history_entries.append({

                        "User": user.name,

                        "PowerShell Command":
                            "Unable to read history",

                        "Error":
                            str(error),

                        "Audit Scan Date":
                            audit_time
                    })


    return history_entries