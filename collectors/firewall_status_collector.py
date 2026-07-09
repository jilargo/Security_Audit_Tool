import subprocess
import re

def get_firewall_status():
    """
    Returns the raw output of the firewall status command.
    """
    try:
        result = subprocess.run(
            ['netsh', 'advfirewall', 'show', 'allprofiles'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except FileNotFoundError:
        return None
    except subprocess.CalledProcessError:
        return "ERROR: Failed to execute command (Run as Administrator)"
    except Exception as e:
        return f"ERROR: {e}"


def print_firewall_status():
    """
    Prints the firewall status in a nice formatted way.
    """
    print("🔍 Checking Windows Firewall Status...\n")
    
    output = get_firewall_status()
    
    if output is None:
        print("❌ Error: 'netsh' command not found. Are you on Windows?")
        return
    elif output.startswith("ERROR"):
        print(output)
        return
    
    # Print full detailed output
    print("=" * 60)
    print("WINDOWS FIREWALL STATUS")
    print("=" * 60)
    print(output)
    
    # Print clean summary
    print("\n📋 SUMMARY:")
    print("-" * 30)
    
    # Extract status for each profile
    if "Domain Profile" in output:
        domain_state = "ON" if "ON" in output.split("Domain Profile")[1][:200] else "OFF"
        print(f"🔹 Domain Profile   : {domain_state}")
    
    if "Private Profile" in output:
        private_state = "ON" if "ON" in output.split("Private Profile")[1][:200] else "OFF"
        print(f"🔹 Private Profile  : {private_state}")
    
    if "Public Profile" in output:
        public_state = "ON" if "ON" in output.split("Public Profile")[1][:200] else "OFF"
        print(f"🔹 Public Profile   : {public_state}")



