import sys
from pathlib import Path
from core.SecurityOperations import SecurityAudit

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QFormLayout, QGroupBox, QDateEdit, QComboBox, QHBoxLayout
)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Security Audit Tool")
        self.resize(700, 400)
        self.setWindowIcon(QIcon("assets/icons/shield.png"))

        self.setup_ui()
        self.load_styles()

    def setup_ui(self):
        """Setup all widgets and layouts"""
        # Title
        title = QLabel("🛡 Security Audit Tool")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setObjectName("title")

        # Inputs 
        self.firstname_input = QLineEdit()
        self.firstname_input.setPlaceholderText("Enter first name")

        self.lastname_input = QLineEdit()
        self.lastname_input.setPlaceholderText("Enter last name")

        self.position_input = QLineEdit()
        self.position_input.setPlaceholderText("Enter position")

        self.company_id_input = QLineEdit()
        self.company_id_input.setPlaceholderText("Enter company ID")

        self.company_email_input = QLineEdit()
        self.company_email_input.setPlaceholderText("Enter company email")

        self.date_hired_input = QDateEdit()
        self.date_hired_input.setCalendarPopup(True)
        self.date_hired_input.setDate(QDate.currentDate())

        self.department_input = QComboBox()
        self.department_input.addItems([
            "IT", "Security", "Human Resources", "Finance",
            "Operations", "Marketing", "Sales"
        ])

        # Form
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.addRow("First Name", self.firstname_input)
        form_layout.addRow("Last Name", self.lastname_input)
        form_layout.addRow("Position", self.position_input)
        form_layout.addRow("Date Hired", self.date_hired_input)
        form_layout.addRow("Company ID", self.company_id_input)
        form_layout.addRow("Department", self.department_input)
        form_layout.addRow("Company Email", self.company_email_input)

        # Group Box
        employee_group = QGroupBox("Employee Details")
        employee_group.setLayout(form_layout)

        # Button
        self.submit_button = QPushButton("Start Security Audit")
        self.submit_button.setMinimumHeight(45)
        self.submit_button.clicked.connect(self.start_security_audit)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.submit_button)
        button_layout.addStretch()

        # Main Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(20)
        layout.addWidget(title)
        layout.addWidget(employee_group)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_styles(self):
        """Load external stylesheet"""
        
        possible_paths = [
            Path("styles/styles.qss"),
            #Path("style.qss"),
            #Path("../styles/styles.qss"),
        ]

        for path in possible_paths:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
                #print(f"✅ Styles loaded from: {path}")
                return

        print("❌ Warning: style.qss file not found! Check the path.")
    

    def start_security_audit(self):
        """Handle submit button click - temporary version"""
        SecurityAudit.generate_audit_report(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())