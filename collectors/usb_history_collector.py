import winreg

def get_usb_history():
    usb_devices = []
    paths = [
        r"SYSTEM\CurrentControlSet\Enum\USBSTOR",
        r"SYSTEM\CurrentControlSet\Enum\USB"
    ]
    
    for reg_path in paths:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            
            for i in range(1000):  # Enumerate subkeys
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey_full_path = f"{reg_path}\\{subkey_name}"
                    subkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey_full_path)
                    
                    for j in range(100):
                        try:
                            device_name = winreg.EnumKey(subkey, j)
                            device_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                                      f"{subkey_full_path}\\{device_name}")
                            
                            # Safely get FriendlyName
                            friendly_name = "Unknown Device"
                            try:
                                friendly_name = winreg.QueryValueEx(device_key, "FriendlyName")[0]
                            except:
                                pass
                            
                            # Get serial / identifier
                            serial = device_name.split("&")[-1] if "&" in device_name else device_name
                            
                            usb_devices.append({
                                "Device Name": friendly_name,
                                "Serial/ID": serial,
                                "Registry Path": subkey_full_path
                            })
                            
                        except OSError:
                            break  # No more devices under this vendor
                except OSError:
                    break  # No more subkeys
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Error accessing {reg_path}: {e}")
    
    return usb_devices


def print_usb_history():
    print("🔌 USB Connection History (Last 10)\n")
    
    devices = get_usb_history()
    
    if not devices:
        print("No USB devices found. Try running as Administrator.")
        return
    
    # Show only the last 10 devices
    last_20 = devices[-20:]   # Takes the last 10 items from the list
    
    print("=" * 80)
    print(f"Showing Last {len(last_20)} USB device(s) out of {len(devices)} total:")
    print("=" * 80)
    
    for idx, dev in enumerate(last_20, 1):
        print(f"{idx:2d}. {dev['Device Name']}")
        print(f"    Serial/ID     : {dev['Serial/ID']}")
        print(f"    Registry Path : {dev['Registry Path']}")
        print("-" * 70)
    
    if len(devices) > 20:
        print(f"\n... and {len(devices) - 20} older USB devices (not shown)")



