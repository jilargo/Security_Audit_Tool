from collectors.system_info_collector import get_system_info

def main():
     sysInfo = get_system_info()

     for key, value in sysInfo.items():
          print(f" {key}: {value}")

if __name__ == "__main__":
    main()