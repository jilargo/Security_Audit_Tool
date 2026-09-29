
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
from pathlib import Path
from datetime import datetime
import pandas as pd
from collections import Counter   # Used for counting top processes

from core.report_style import ReportStyler   # All visual formatting lives here


class SecurityAudit:
    """
    Core class responsible for generating a professional Security Audit Report.
    
    This class collects data from the GUI form and various system collectors,
    then compiles everything into a well-formatted, visually appealing Excel report
    with a dashboard, risk assessment, and charts.
    """

    @staticmethod
    def get_form_data(window):
        """
        Extract all the information entered by the user in the MainWindow GUI.
        
        Args:
            window: The MainWindow instance containing the input fields
            
        Returns:
            dict: Employee and audit context data
        """
        data = {
            "first_name": window.firstname_input.text().strip(),
            "last_name": window.lastname_input.text().strip(),
            "position": window.position_input.text().strip(),
            "company_id": window.company_id_input.text().strip(),
            "company_email": window.company_email_input.text().strip(),
            "date_hired": window.date_hired_input.date().toString("yyyy-MM-dd"),
            "Department": window.department_input.currentText(),
        }
        return data

    @staticmethod
    def generate_audit_report(window=None, output_folder="reports", logo_path=None,
                              progress=None, employee_data=None):
        """
        Main method that generates the complete security audit Excel report.
        
        Process flow:
        1. Collect employee data (supplied by the GUI, or read from `window`)
        2. Gather system security information from various collectors
        3. Assess risk level based on findings
        4. Create Excel file with multiple sheets using pandas
        5. Apply advanced formatting, charts, and logo using openpyxl
        6. Save and return the file path
        
        Args:
            window: Optional MainWindow instance, only used when employee_data is omitted
            output_folder: Folder where the report will be saved
            logo_path: Optional path to company logo image
            progress: Optional callable(percent, message) used to report progress
            employee_data: Optional dict of employee details captured on the GUI thread
            
        Returns:
            Path: Full path to the generated Excel report
        """
        def tick(percent, message):
            """Forward a progress update to the caller, if it wants one."""
            if progress:
                progress(percent, message)

        # Step 1: Get employee/auditor information
        employee_data = employee_data or SecurityAudit.get_form_data(window)
        tick(5, "Reading auditor details")
        
        # Step 2: Import and call all data collectors
        # (Re-importing here ensures fresh data and avoids circular imports)
        from collectors.imports import (
            get_antivirus_info, get_system_events, get_firewall_status,
            get_installed_applications, get_network_connections,
            get_powershell_history, get_running_processes, get_scheduled_tasks,
            get_startup_programs, get_system_info, get_usb_history, get_local_users
        )
        
        # Collect all security-related system information
        tick(10, "Collecting antivirus information")
        antivirus_info = get_antivirus_info()
        tick(16, "Reading Windows event logs")
        event_logs_info = get_system_events()
        tick(22, "Checking firewall status")
        firewall_status = get_firewall_status()
        tick(28, "Reading installed applications")
        installed_apps = get_installed_applications()
        tick(34, "Inspecting network connections")
        network_connections = get_network_connections()
        tick(40, "Reading PowerShell history")
        powershell_history = get_powershell_history()
        tick(46, "Enumerating running processes")
        running_process = get_running_processes()
        tick(52, "Enumerating scheduled tasks")
        scheduled_task = get_scheduled_tasks()
        tick(58, "Reading startup programs")
        start_up_task = get_startup_programs()
        tick(64, "Collecting system information")
        system_info = get_system_info()
        tick(70, "Reading USB device history")
        usb_history = get_usb_history()
        tick(76, "Auditing local user accounts")
        local_users = get_local_users()
        tick(80, "Assessing risk level")
        
        # Ensure output directory exists (relative paths resolve to the project root)
        output_path = Path(output_folder)
        if not output_path.is_absolute():
            output_path = Path(__file__).resolve().parent.parent / output_path
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Security_Audit_{employee_data['first_name']}_{employee_data['last_name']}_{timestamp}.xlsx"
        filepath = output_path / filename

        # === Step 3: Dynamic Risk Level Assessment ===
        # Count potentially suspicious running processes
        suspicious_count = sum(1 for p in running_process 
                             if any(x in str(p).lower() for x in 
                                   ['powershell', 'cmd.exe', 'mshta', 'wscript', 'cscript']))
        
        firewall_str = str(firewall_status).upper()
        
        # Determine overall risk level based on multiple factors
        if suspicious_count >= 5 or "OFF" in firewall_str or "DISABLED" in firewall_str:
            risk_level = "CRITICAL"
        elif suspicious_count >= 3 or len(running_process) > 250:
            risk_level = "HIGH"
        elif suspicious_count >= 1:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # === Step 4: Create Excel File with pandas ===
        tick(86, "Building report worksheets")
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            
            # Dashboard Sheet - rebuilt as a cover page during formatting
            pd.DataFrame({"Metric": ["Placeholder"], "Value": [""]}).to_excel(
                writer, sheet_name="Dashboard", index=False)

            # Employee Info Sheet
            pd.DataFrame([employee_data]).to_excel(writer, sheet_name="Employee Info", index=False)
            
            # Antivirus Information
            pd.DataFrame([antivirus_info.get("Windows_Defender", {})]).to_excel(
                writer, sheet_name="Windows Defender", index=False)
            
            if antivirus_info.get("Other_Antivirus"):
                pd.DataFrame(antivirus_info["Other_Antivirus"]).to_excel(
                    writer, sheet_name="Other Antivirus", index=False)
            else:
                pd.DataFrame([{"Message": "No other antivirus detected"}]).to_excel(
                    writer, sheet_name="Other Antivirus", index=False)
            
            # All other detailed sheets
            pd.DataFrame(event_logs_info).to_excel(writer, sheet_name="Windows Events", index=False)
            pd.DataFrame([{"Firewall Status": firewall_status}]).to_excel(writer, sheet_name="Firewall Status", index=False)
            pd.DataFrame(installed_apps).to_excel(writer, sheet_name="Installed Apps List", index=False)
            pd.DataFrame(network_connections).to_excel(writer, sheet_name="Network Connections", index=False)
            pd.DataFrame(powershell_history).to_excel(writer, sheet_name="Powershell History", index=False)
            pd.DataFrame(running_process).to_excel(writer, sheet_name="Running Processes", index=False)
            pd.DataFrame(scheduled_task).to_excel(writer, sheet_name="Scheduled Tasks", index=False)
            pd.DataFrame(start_up_task).to_excel(writer, sheet_name="Startup Programs", index=False)
            
            pd.DataFrame(list(system_info.items()), columns=["System Attribute", "Details"]).to_excel(
                writer, sheet_name="System Information", index=False)
            
            pd.DataFrame(usb_history).to_excel(writer, sheet_name="USB History", index=False)
            pd.DataFrame(local_users).to_excel(writer, sheet_name="Local Users", index=False)

        # === Step 5: Prepare dashboard aggregates ===
        process_list = []
        for p in running_process:
            if isinstance(p, dict):
                name = p.get('Name') or p.get('name', 'Unknown')
            else:
                name = str(p)
            if name and name != 'None':
                clean_name = str(name).split('.')[0][:25]  # Clean and truncate
                process_list.append(clean_name)

        # Count occurrences and get top 10
        top_10 = Counter(process_list).most_common(10)

        # === Step 5: Hand the workbook to the report designer ===
        tick(94, "Applying report design and charts")
        wb = load_workbook(filepath)

        ReportStyler.apply(
            wb,
            employee_data=employee_data,
            computer_name=system_info.get('Computer Name', 'N/A'),
            risk_level=risk_level,
            firewall_text=firewall_status,
            defender_status=antivirus_info.get("Windows_Defender", {}),
            suspicious_processes=suspicious_count,
            top_processes=top_10,
        )

        # Add company logo to Dashboard (if provided), clear of the designed grid
        if logo_path and Path(logo_path).exists():
            try:
                img = Image(logo_path)
                img.width = 180
                img.height = 90
                wb["Dashboard"].add_image(img, 'J1')
            except Exception as e:
                print(f"⚠️ Could not add logo: {e}")

        # Save the final formatted workbook
        tick(99, "Saving report to disk")
        wb.save(filepath)
        
        
        
        return filepath
    
    #Author: James Ian Largo
    #Purpose: For Future Use