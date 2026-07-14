# 🛡 Security Audit Tool

A lightweight **Windows security auditing utility** designed to collect, analyze, and generate audit reports containing important system-level security information.

The Security Audit Tool helps IT administrators, security teams, and individuals perform basic endpoint security assessments by gathering system artifacts such as event logs, running processes, network activity, user accounts, and security configurations.

The goal of this project is to provide a simple way to create **visual and structured security audit trails** that can assist with system monitoring, troubleshooting, and security reviews.

---

# 🚀 Features

The tool performs automated security audits across multiple areas of a Windows system:

## 🔐 Security Information
- **Antivirus Information**
  - Detect installed antivirus/security products
  - Review endpoint protection status

- **Firewall Status**
  - Collect Windows Firewall configuration
  - Check enabled firewall profiles

- **User Account Audit**
  - Gather local user account information
  - Review available system accounts

---

## 📊 System Monitoring

- **System Information**
  - Collect operating system details
  - Capture hardware and environment information

- **Running Process Logs**
  - List currently running processes
  - Assist in identifying suspicious applications

- **Startup Applications**
  - Identify programs configured to run during system startup

- **Scheduled Tasks**
  - Collect scheduled task information
  - Review automated processes configured on the system

---

## 🌐 Network & Activity Auditing

- **Network Connection Logs**
  - Monitor active network connections
  - Capture communication endpoints

- **PowerShell History**
  - Collect PowerShell command history
  - Assist in detecting suspicious administrative activity

- **Event Logs**
  - Gather Windows event logs
  - Review system activities and security-related events

- **USB History Logs**
  - Track previously connected USB devices
  - Assist with removable media auditing

---

# 📋 Audit Report Generation

The collected information is organized into structured reports for easier review and documentation.

Generated reports include information such as:

- Employee/System Identification
- Security Configuration
- System Activities
- Network Information
- User Activity Indicators
- Potential Security Concerns

---

# 🛠 Technology Stack

Built using:

- **Python**
- **PySide6** - Desktop GUI Framework
- **Pandas / OpenPyXL** - Report Generation
- **psutil** - System and Network Monitoring
- **Windows APIs / Registry Access** - System Information Collection

---

# 📦 Installation

## Clone the Repository

```bash
git clone https://github.com/yourusername/security-audit-tool.git
```

## Navigate to Project Directory

```bash
cd security-audit-tool
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
python main.py
```



# 🎯 Use Cases

This tool can be useful for:

- IT asset auditing
- Endpoint security assessment
- Security awareness exercises
- Basic incident investigation
- System troubleshooting
- Internal security reviews

---

# ⚠️ Disclaimer

This tool is intended for **authorized security auditing and system administration purposes only**.

Always obtain proper permission before collecting system information from any device.

---

# 📌 Future Improvements

Possible future enhancements:

- [ ] Add threat detection rules
- [ ] Add suspicious process analysis
- [ ] Add hash checking for executable files
- [ ] Add vulnerability assessment features
- [ ] Add JSON/CSV export support
- [ ] Add centralized audit management
- [ ] Add SIEM integration support

---

# 👨‍💻 Author

Developed as a cybersecurity learning project focused on endpoint auditing, system monitoring, and security automation.
