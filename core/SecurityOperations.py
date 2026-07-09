from collectors.antivirus_info_collector import get_antivirus_info
from pathlib import Path
from datetime import datetime
import json
import pandas as pd

class SecurityAudit:
    
    
    @staticmethod
    def get_form_data(window):
        """Collect data from MainWindow form fields"""
        data = {
            "first_name": window.firstname_input.text().strip(),
            "last_name": window.lastname_input.text().strip(),
            "position": window.position_input.text().strip(),
            "company_id": window.company_id_input.text().strip(),
            "company_email": window.company_email_input.text().strip(),
            "date_hired": window.date_hired_input.date().toString("yyyy-MM-dd"),
            "department": window.department_input.currentText(),
        }
        return data
    
    @staticmethod
    def generate_audit_report(window, output_folder="reports"):
        """Generate full audit report as Excel file"""
        
        # 1. Get Employee Data
        employee_data = SecurityAudit.get_form_data(window)
        
        # 2. Get Antivirus Info
        antivirus_info = get_antivirus_info()
        
        # Create output folder
        Path(output_folder).mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Security_Audit_{employee_data['first_name']}_{employee_data['last_name']}_{timestamp}.xlsx"
        filepath = Path(output_folder) / filename

        # Prepare data for Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            
            # Sheet 1: Employee Information
            emp_df = pd.DataFrame([employee_data])
            emp_df.to_excel(writer, sheet_name="Employee Info", index=False)
            
            # Sheet 2: Windows Defender
            defender_df = pd.DataFrame([antivirus_info["Windows_Defender"]])
            defender_df.to_excel(writer, sheet_name="Windows Defender", index=False)
            
            # Sheet 3: Other Antivirus
            if antivirus_info["Other_Antivirus"]:
                other_av_df = pd.DataFrame(antivirus_info["Other_Antivirus"])
                other_av_df.to_excel(writer, sheet_name="Other Antivirus", index=False)
            else:
                pd.DataFrame([{"Message": "No other antivirus detected"}]).to_excel(
                    writer, sheet_name="Other Antivirus", index=False
                )

        print(f"✅ Audit Report generated successfully!")
        print(f"📁 File saved as: {filepath}")
        
        return filepath
        