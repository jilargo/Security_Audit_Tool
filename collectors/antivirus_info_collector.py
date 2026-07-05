import subprocess
import json

def get_antivirus_info():
    """
    Get information about installed antivirus / security products.
    """
    info = {
        "Windows_Defender": {},
        "Other_Antivirus": []
    }
    
    # 1. Check Windows Defender Status
    try:
        result = subprocess.run(
            ['powershell', '-Command', 
             'Get-MpComputerStatus | Select-Object AMServiceEnabled, AntivirusEnabled, '
             'RealTimeProtectionEnabled, AntivirusSignatureLastUpdated | ConvertTo-Json'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout.strip():
            defender = json.loads(result.stdout)
            info["Windows_Defender"] = {
                "Real-time Protection": "✅ Enabled" if defender.get("RealTimeProtectionEnabled") else "❌ Disabled",
                "Antivirus Service": "✅ Enabled" if defender.get("AntivirusEnabled") else "❌ Disabled",
                "Signature Updated": defender.get("AntivirusSignatureLastUpdated", "Unknown")
            }
    except:
        info["Windows_Defender"] = {"Status": "Could not retrieve (try running as Admin)"}
    
    # 2. Check all Security Products via WMI
    try:
        result = subprocess.run(
            ['wmic', '/Namespace:\\root\\SecurityCenter2', 'path', 'AntivirusProduct', 
             'get', 'displayName,productState,timestamp', '/format:list'],
            capture_output=True,
            text=True,
            timeout=8
        )
        
        output = result.stdout.strip()
        if output:
            # Parse multiple AV products
            products = output.split('\n\n')
            for product in products:
                if product.strip():
                    lines = product.strip().split('\n')
                    av = {}
                    for line in lines:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            av[key.strip()] = value.strip()
                    if av:
                        info["Other_Antivirus"].append(av)
    except:
        pass
    
    return info


def print_antivirus_status():
    print("🛡️  Antivirus / Security Status\n")
    
    data = get_antivirus_info()
    
    # Windows Defender
    print("=" * 60)
    print("WINDOWS DEFENDER")
    print("=" * 60)
    defender = data["Windows_Defender"]
    
    if isinstance(defender, dict) and "Real-time Protection" in defender:
        for key, value in defender.items():
            print(f"{key:25}: {value}")
    else:
        print("Status: Unable to retrieve Defender info")
    
    # Other Antivirus Products
    print("\n" + "=" * 60)
    print("OTHER ANTIVIRUS PRODUCTS")
    print("=" * 60)
    
    if data["Other_Antivirus"]:
        for i, av in enumerate(data["Other_Antivirus"], 1):
            name = av.get("displayName", "Unknown")
            print(f"{i}. {name}")
            for key, value in av.items():
                if key != "displayName":
                    print(f"   {key:20}: {value}")
            print("-" * 50)
    else:
        print("No other third-party antivirus detected.")
    
    



print_antivirus_status()