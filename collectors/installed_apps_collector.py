import winreg

UNINSTALL_PATHS = [
    (
        "HKLM",
        winreg.HKEY_LOCAL_MACHINE,
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
    ),
    (
        "HKLM",
        winreg.HKEY_LOCAL_MACHINE,
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ),
    (
        "HKCU",
        winreg.HKEY_CURRENT_USER,
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
    )
]

def get_registry_value(key, value_name):
    """
    Safely retrieve a registry value.

    Returns None if the value does not exist.
    """
    try:
        return winreg.QueryValueEx(key, value_name)[0]
    except FileNotFoundError:
        return None


def get_installed_applications():

    applications = []

    for hive_name, hive, path in UNINSTALL_PATHS:

        try:
            root_key = winreg.OpenKey(hive, path)

        except FileNotFoundError:
            continue

        number_of_programs = winreg.QueryInfoKey(root_key)[0]

        for index in range(number_of_programs):

            try:

                subkey_name = winreg.EnumKey(root_key, index)

                program_key = winreg.OpenKey(root_key, subkey_name)

                display_name = get_registry_value(
                    program_key,
                    "DisplayName"
                )

                if not display_name:
                    continue

                application = {
                    "DisplayName": display_name,
                    "DisplayVersion": get_registry_value(program_key, "DisplayVersion"),
                    "Publisher": get_registry_value(program_key, "Publisher"),
                    "InstallDate": get_registry_value(program_key, "InstallDate"),
                    "InstallLocation": get_registry_value(program_key, "InstallLocation"),
                    "UninstallString": get_registry_value(program_key, "UninstallString"),
                    "RegistryHive": hive_name,
                    "RegistryPath": path
                }

                applications.append(application)

            except OSError:
                continue

    return applications

def print_installed_apps():
    installed_apps = get_installed_applications()
    print(f"\nFound {len(installed_apps)} applications.\n")

    for app in installed_apps:
        print("-" * 50)
        for key, value in app.items():
            print(f"{key}: {value}")
            