import subprocess
import json


def get_scheduled_tasks():
    """
    Returns a list of Windows Scheduled Tasks.
    """

    powershell_command = r"""
    Get-ScheduledTask |
    Select-Object TaskName, TaskPath, State, Author |
    ConvertTo-Json -Depth 2
    """

    try:
        result = subprocess.run(
            ["powershell", "-Command", powershell_command],
            capture_output=True,
            text=True,
            check=True
        )

        if not result.stdout.strip():
            return []

        tasks = json.loads(result.stdout)

        # If only one task exists, PowerShell returns a dict instead of a list
        if isinstance(tasks, dict):
            tasks = [tasks]

        return tasks

    except subprocess.CalledProcessError as e:
        print("PowerShell Error:")
        print(e.stderr)
        return []

    except Exception as e:
        print(e)
        return []


def print_scheduled_tasks():

    tasks = get_scheduled_tasks()

    print(f"\nFound {len(tasks)} Scheduled Tasks\n")

    for index, task in enumerate(tasks, start=1):

        print("=" * 60)
        print(f"Task #{index}")
        print(f"Task Name : {task.get('TaskName')}")
        print(f"Task Path : {task.get('TaskPath')}")
        print(f"State     : {task.get('State')}")
        print(f"Author    : {task.get('Author')}")


