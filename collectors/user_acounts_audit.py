import subprocess
import json


def get_local_users():
    """
    Retrieves all local Windows user accounts.
    """

    powershell_command = r"""
    Get-LocalUser |
    Select-Object `
        Name,
        FullName,
        Enabled,
        @{Name="LastLogon";Expression={
            if ($_.LastLogon) {
                $_.LastLogon.ToString("MMMM dd, yyyy hh:mm:ss tt")
            }
            else {
                "Never"
            }
        }},
        PasswordRequired,
        PasswordExpires,
        UserMayChangePassword |
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

        users = json.loads(result.stdout)

        # If only one user exists, PowerShell returns an object instead of a list
        if isinstance(users, dict):
            users = [users]

        return users

    except subprocess.CalledProcessError as e:
        print("PowerShell Error:")
        print(e.stderr)
        return []

    except Exception as e:
        print(f"Error: {e}")
        return []


def print_local_users():
    users = get_local_users()

    print("\n" + "=" * 70)
    print("LOCAL USER ACCOUNTS AUDIT")
    print("=" * 70)
    print(f"Found {len(users)} local user account(s).\n")

    for index, user in enumerate(users, start=1):

        print("-" * 70)
        print(f"User #{index}")
        print("-" * 70)
        print(f"Username                : {user.get('Name')}")
        print(f"Full Name               : {user.get('FullName') or 'N/A'}")
        print(f"Account Enabled         : {user.get('Enabled')}")
        print(f"Last Logon              : {user.get('LastLogon')}")
        print(f"Password Required       : {user.get('PasswordRequired')}")
        print(f"Password Expires        : {user.get('PasswordExpires')}")
        print(f"User Can Change Password: {user.get('UserMayChangePassword')}")

    print("\nAudit Complete.")


