import os
import winreg


REGISTRY_PATHS = [

    ("HKCU",
     winreg.HKEY_CURRENT_USER,
     r"Software\Microsoft\Windows\CurrentVersion\Run"),

    ("HKLM",
     winreg.HKEY_LOCAL_MACHINE,
     r"Software\Microsoft\Windows\CurrentVersion\Run")
]


def get_registry_startup_programs():

    startup_items = []

    for hive_name, hive, path in REGISTRY_PATHS:

        try:

            key = winreg.OpenKey(hive, path)

        except FileNotFoundError:
            continue

        value_count = winreg.QueryInfoKey(key)[1]

        for index in range(value_count):

            name, command, _ = winreg.EnumValue(key, index)

            startup_items.append({

                "Location": "Registry",

                "RegistryHive": hive_name,

                "Name": name,

                "Command": command

            })

    return startup_items

def get_startup_folder_programs():

    startup_items = []

    folders = [

        (
            "Current User",
            os.path.expandvars(
                r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
            )
        ),

        (
            "All Users",
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp"
        )
    ]

    for owner, folder in folders:

        if not os.path.exists(folder):
            continue

        for filename in os.listdir(folder):

            startup_items.append({

                "Location": "Startup Folder",

                "Owner": owner,

                "Name": filename,

                "Path": os.path.join(folder, filename)

            })

    return startup_items

def get_startup_programs():

    startup_programs = []

    startup_programs.extend(
        get_registry_startup_programs()
    )

    startup_programs.extend(
        get_startup_folder_programs()
    )

    return startup_programs

def print_startup_programs():

    startup = get_startup_programs()

    print(f"\nFound {len(startup)} startup items.\n")

    for index, item in enumerate(startup, start=1):

        print("=" * 60)

        print(f"Startup Item #{index}")

        for key, value in item.items():

            print(f"{key}: {value}")


print_startup_programs()