import sys
import os
import webbrowser
from PySide6.QtCore import Qt, QDate, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QFormLayout, QGroupBox, QDateEdit, QComboBox,
    QHBoxLayout, QMessageBox, QProgressBar, QDialog
)

from core.SecurityOperations import SecurityAudit   # ← Import from core


class AuditWorker(QThread):
    progress = Signal(int)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, window):
        super().__init__()
        self.window = window

    def run(self):
        try:
            self.progress.emit(10)
            filepath = SecurityAudit.generate_audit_report(self.window)
            self.progress.emit(100)
            self.finished.emit(str(filepath))
        except Exception as e:
            self.error.emit(str(e))


class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Security Audit")
        self.setFixedSize(420, 160)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        self.label = QLabel("Running comprehensive security audit...\nPlease wait.")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("", 11))

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)

        layout.addWidget(self.label)
        layout.addWidget(self.progress)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Security Audit Tool")
        self.resize(720, 500)
        self.setup_ui()

    def setup_ui(self):
        title = QLabel("🛡 Security Audit Tool")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)

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
        self.department_input.addItems(["IT", "Security", "Human Resources", "Finance", "Operations", "Marketing", "Sales"])

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(12)
        form_layout.addRow("First Name *", self.firstname_input)
        form_layout.addRow("Last Name *", self.lastname_input)
        form_layout.addRow("Position *", self.position_input)
        form_layout.addRow("Company ID *", self.company_id_input)
        form_layout.addRow("Company Email *", self.company_email_input)
        form_layout.addRow("Date Hired", self.date_hired_input)
        form_layout.addRow("Department", self.department_input)

        group = QGroupBox("Employee Information")
        group.setLayout(form_layout)

        self.submit_button = QPushButton("🚀 Start Security Audit")
        self.submit_button.setMinimumHeight(55)
        self.submit_button.clicked.connect(self.start_security_audit)

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        layout.addWidget(title)
        layout.addWidget(group)
        layout.addStretch()
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def validate_inputs(self):
        required = [
            (self.firstname_input, "First Name"),
            (self.lastname_input, "Last Name"),
            (self.position_input, "Position"),
            (self.company_id_input, "Company ID"),
            (self.company_email_input, "Company Email")
        ]
        for widget, name in required:
            if not widget.text().strip():
                QMessageBox.warning(self, "Required", f"{name} is required!")
                widget.setFocus()
                return False
        return True

    def start_security_audit(self):
        if not self.validate_inputs():
            return

        self.loading = LoadingDialog(self)
        self.loading.show()

        self.worker = AuditWorker(self)
        self.worker.progress.connect(self.loading.progress.setValue)
        self.worker.finished.connect(self.on_audit_finished)
        self.worker.error.connect(self.on_audit_error)
        self.worker.start()

        self.setEnabled(False)

    def on_audit_finished(self, filepath):
        self.loading.close()
        self.setEnabled(True)

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Success")
        msg.setText("Security Audit Completed!")
        msg.setInformativeText(f"Report saved successfully.\n\n{filepath}")

        open_btn = msg.addButton("Open Report", QMessageBox.ActionRole)
        msg.addButton("OK", QMessageBox.AcceptRole)

        msg.exec()

        if msg.clickedButton() == open_btn:
            try:
                os.startfile(filepath)
            except:
                webbrowser.open(filepath)

    def on_audit_error(self, error_msg):
        self.loading.close()
        self.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Failed to generate report:\n{error_msg}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())