import sys
import os
import webbrowser
from pathlib import Path
from PySide6.QtCore import Qt, QDate, QThread, Signal
from PySide6.QtGui import QFont, QIcon, QMovie
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QFormLayout, QGroupBox, QDateEdit, QComboBox,
    QMessageBox, QProgressBar, QDialog
)

# Import the core security audit functionality from the project's core module
from core.SecurityOperations import SecurityAudit   # ← Import from core


class AuditWorker(QThread):
    """
    Worker thread to run the security audit in the background.
    This prevents the GUI from freezing during the potentially long-running audit process.
    """
    # Custom signals to communicate with the main GUI thread
    progress = Signal(int)      # Emits progress percentage (0-100)
    finished = Signal(str)      # Emits the path to the generated report
    error = Signal(str)         # Emits error message if something goes wrong

    def __init__(self, window):
        super().__init__()
        self.window = window  # Reference to the main window to access form data

    def run(self):
        """Main execution method for the worker thread (runs in background)."""
        try:
            self.progress.emit(10)  # Indicate audit has started
            # Generate the audit report using data from the main window
            filepath = SecurityAudit.generate_audit_report(self.window)
            self.progress.emit(100)  # Mark completion
            self.finished.emit(str(filepath))  # Send report path back to GUI
        except Exception as e:
            self.error.emit(str(e))  # Send any error to be displayed


class LoadingDialog(QDialog):
    """
    Modal dialog shown during the security audit.
    Displays an animated GIF, status text, and progress bar.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Security Audit")
        self.setFixedSize(480, 260)
        
        # Make it modal (blocks interaction with main window) and remove close button
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # === GIF Animation ===
        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignCenter)
        
        # Load animated GIF (sand timer) - update path if your asset location changes
        self.movie = QMovie("assets/icons/sandTimer.gif")  
        self.gif_label.setMovie(self.movie)
        self.movie.start()   # Start the animation

        # Loading message
        self.label = QLabel("Running comprehensive security audit...\nPlease wait.")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("", 11))

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)

        layout.addWidget(self.gif_label)
        layout.addWidget(self.label)
        layout.addWidget(self.progress)

        # Clean up animation when dialog is destroyed
        self.destroyed.connect(self.stop_gif)

    def stop_gif(self):
        """Stop the GIF animation to free resources."""
        if hasattr(self, 'movie'):
            self.movie.stop()


class MainWindow(QWidget):
    """
    Main application window for the Security Audit Tool.
    Contains the input form and handles user interactions.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Security Audit Tool / James Ian Largo")
        self.resize(720, 500)
        self.setWindowIcon(QIcon("assets/icons/shield.png"))
        self.setup_ui()
        self.load_stylesheet()

    def setup_ui(self):
        """Set up all widgets and layouts for the main interface."""
        # Title label with custom styling
        title = QLabel("🛡 Security Audit Tool")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1E88E5;")
        
        title_font = QFont()
        title_font.setPointSize(26)
        title_font.setBold(True)
        title.setFont(title_font)
        
        # Input fields
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

        # Form layout for clean label + field alignment
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(12)
        form_layout.addRow("First Name *", self.firstname_input)
        form_layout.addRow("Last Name *", self.lastname_input)
        form_layout.addRow("Position *", self.position_input)
        form_layout.addRow("Company ID *", self.company_id_input)
        form_layout.addRow("Company Email *", self.company_email_input)
        form_layout.addRow("Date Hired", self.date_hired_input)
        form_layout.addRow("Department", self.department_input)

        # Group box to visually group employee information
        group = QGroupBox("Employee Information")
        group.setLayout(form_layout)

        # Submit button with emoji and larger size for prominence
        self.submit_button = QPushButton("🚀 Start Security Audit")
        self.submit_button.setMinimumHeight(55)
        self.submit_button.setMinimumWidth(55)
        self.submit_button.clicked.connect(self.start_security_audit)

        # Main vertical layout
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        layout.addWidget(title)
        layout.addWidget(group)
        layout.addStretch()          # Pushes button to bottom
        layout.addWidget(self.submit_button)

        self.setLayout(layout)
    
    def load_stylesheet(self):
        """Load external QSS stylesheet for consistent theming."""
        possible_paths = [
            Path("styles/styles.qss"),
            # Path("styles.qss"),
            # Path("../styles/styles.qss"),
        ]
        
        for path in possible_paths:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
                return
        print("⚠️ Warning: styles.qss file not found!")
        
    def validate_inputs(self):
        """Check that all required fields are filled before starting audit."""
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
        """Validate inputs, show loading dialog, and start background audit worker."""
        if not self.validate_inputs():
            return

        # Show loading dialog
        self.loading = LoadingDialog(self)
        self.loading.show()

        # Create and start background worker
        self.worker = AuditWorker(self)
        self.worker.progress.connect(self.loading.progress.setValue)
        self.worker.finished.connect(self.on_audit_finished)
        self.worker.error.connect(self.on_audit_error)
        self.worker.start()

        # Disable main window while audit runs
        self.setEnabled(False)

    def on_audit_finished(self, filepath):
        """Handle successful completion of the audit."""
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

        # Open the generated report if user clicks the button
        if msg.clickedButton() == open_btn:
            try:
                os.startfile(filepath)      # Windows native open
            except:
                webbrowser.open(filepath)   # Fallback for other OSes

    def on_audit_error(self, error_msg):
        """Handle errors during the audit process."""
        self.loading.close()
        self.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Failed to generate report:\n{error_msg}")


if __name__ == "__main__":
    # Standard PySide6 application entry point
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())