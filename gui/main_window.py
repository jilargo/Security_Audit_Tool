"""
Security Audit Tool - graphical interface.

Layout: a branded header, scrollable card-based body (employee details +
audit coverage) and a sticky footer that holds the primary call to action.
All visual styling lives in styles/styles.qss.
"""

import os
import re
import sys
import webbrowser
from pathlib import Path

from PySide6.QtCore import Qt, QDate, QThread, Signal, QUrl
from PySide6.QtGui import QColor, QFont, QIcon, QMovie, QPalette, QPixmap
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QScrollArea,
    QComboBox, QDateEdit, QMessageBox, QProgressBar, QDialog,
    QSizePolicy,
)

# Import the core security audit functionality from the project's core module
from core.SecurityOperations import SecurityAudit

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets" / "icons"
STYLES_PATH = BASE_DIR / "styles" / "styles.qss"

AUDIT_COVERAGE = [
    "Antivirus", "Firewall Status", "Windows Events", "Running Processes",
    "Network Connections", "PowerShell History", "Scheduled Tasks",
    "Startup Programs", "Installed Applications", "USB History",
    "Local Users", "System Information",
]


class AuditWorker(QThread):
    """
    Worker thread to run the security audit in the background.
    This prevents the GUI from freezing during the potentially long-running audit process.
    """
    # Custom signals to communicate with the main GUI thread
    progress = Signal(int, str)  # Emits progress percentage (0-100) and the current step
    finished = Signal(str)        # Emits the path to the generated report
    error = Signal(str)          # Emits error message if something goes wrong

    def __init__(self, employee_data):
        super().__init__()
        self.employee_data = employee_data  # Snapshot taken on the GUI thread

    def run(self):
        """Main execution method for the worker thread (runs in background)."""
        try:
            self.progress.emit(2, "Preparing audit engine")
            # Generate the audit report using the employee data captured earlier
            filepath = SecurityAudit.generate_audit_report(
                employee_data=self.employee_data,
                progress=lambda percent, message: self.progress.emit(percent, message),
            )
            self.progress.emit(100, "Audit complete")
            self.finished.emit(str(filepath))  # Send report path back to GUI
        except Exception as e:
            self.error.emit(str(e))  # Send any error to be displayed


class LoadingDialog(QDialog):
    """
    Modal dialog shown during the security audit.
    Displays an animated GIF, the live step, and a progress bar.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Security Audit")
        self.setObjectName("loadingDialog")
        self.setFixedSize(540, 250)

        # Make it modal (blocks interaction with main window) and remove close button
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 24)
        layout.setSpacing(0)

        header = QHBoxLayout()
        header.setSpacing(16)

        # === GIF Animation ===
        self.gif_label = QLabel()
        self.gif_label.setFixedSize(56, 56)
        self.gif_label.setAlignment(Qt.AlignCenter)

        # Load animated GIF (sand timer)
        self.movie = QMovie(str(ASSETS_DIR / "sandTimer.gif"))
        if self.movie.isValid():
            frame_size = self.movie.currentImage().size()
            if not frame_size.isEmpty():
                self.movie.setScaledSize(frame_size.scaled(56, 56, Qt.KeepAspectRatio))
            self.gif_label.setMovie(self.movie)
            self.movie.start()  # Start the animation

        header.addWidget(self.gif_label, 0, Qt.AlignTop)

        text_column = QVBoxLayout()
        text_column.setSpacing(14)

        title = QLabel("Security audit in progress")
        title.setObjectName("loadingTitle")

        # Live status line - updated by the worker thread
        self.step_label = QLabel("Starting up...")
        self.step_label.setObjectName("loadingStep")
        self.step_label.setWordWrap(True)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setObjectName("auditProgress")
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)

        text_column.addWidget(title)
        text_column.addWidget(self.step_label)
        text_column.addWidget(self.progress)
        header.addLayout(text_column, 1)

        layout.addLayout(header)
        layout.addSpacing(18)

        note = QLabel("Artifacts are collected read-only. Keep this window open until the report is ready.")
        note.setObjectName("loadingNote")
        note.setWordWrap(True)
        layout.addWidget(note)

        # Clean up animation when dialog is destroyed
        self.destroyed.connect(self.stop_gif)

    def set_progress(self, value, message=None):
        """Update the progress bar and the status line."""
        self.progress.setValue(int(value))
        if message:
            self.step_label.setText(message)

    def stop_gif(self):
        """Stop the GIF animation to free resources."""
        if hasattr(self, 'movie'):
            self.movie.stop()


class Card(QFrame):
    """White rounded surface with an accent bar, a heading and a body layout."""

    def __init__(self, title, subtitle="", parent=None):
        super().__init__(parent)
        self.setObjectName("card")

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 20)
        root.setSpacing(14)

        header = QHBoxLayout()
        header.setSpacing(12)

        accent = QFrame()
        accent.setObjectName("accentBar")
        accent.setFixedWidth(4)
        accent.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        header.addWidget(accent)

        headings = QVBoxLayout()
        headings.setSpacing(2)
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        headings.addWidget(title_label)
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName("cardSubtitle")
            subtitle_label.setWordWrap(True)
            headings.addWidget(subtitle_label)
        header.addLayout(headings, 1)

        root.addLayout(header)

        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFixedHeight(1)
        root.addWidget(divider)

        self.body = QVBoxLayout()
        self.body.setContentsMargins(0, 0, 0, 0)
        self.body.setSpacing(12)
        root.addLayout(self.body)


class MainWindow(QWidget):
    """
    Main application window for the Security Audit Tool.
    Contains the input form and handles user interactions.
    """
    def __init__(self):
        super().__init__()
        self.setObjectName("root")
        self.setWindowTitle("Security Audit Tool / James Ian Largo")
        self.setWindowIcon(QIcon(str(ASSETS_DIR / "shield.png")))
        self.setFont(QFont("Segoe UI", 10))
        self.setMinimumSize(780, 560)
        self.resize(880, 700)
        self.setup_ui()
        self.apply_palette()
        self.load_stylesheet()

    def apply_palette(self):
        """
        Soften the placeholder colour. Qt ignores the ::placeholder style-sheet
        pseudo-state, so the palette role is used instead.
        """
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#A8B4C4"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#0F172A"))
        self.setPalette(palette)

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    def setup_ui(self):
        """Set up all widgets and layouts for the main interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.build_header())
        layout.addWidget(self.build_header_accent())
        layout.addWidget(self.build_body(), 1)
        layout.addWidget(self.build_footer())

    def build_header(self):
        """Branded application banner."""
        header = QWidget()
        header.setObjectName("header")

        layout = QVBoxLayout(header)
        layout.setContentsMargins(28, 22, 28, 22)
        layout.setSpacing(0)

        row = QHBoxLayout()
        row.setSpacing(16)

        logo = QLabel()
        logo.setFixedSize(46, 46)
        logo.setAlignment(Qt.AlignCenter)
        shield = QPixmap(str(ASSETS_DIR / "shield.png"))
        if not shield.isNull():
            logo.setPixmap(shield.scaled(46, 46, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        row.addWidget(logo, 0, Qt.AlignVCenter)

        titles = QVBoxLayout()
        titles.setSpacing(3)

        title = QLabel("Security Audit Tool")
        title.setObjectName("appTitle")

        subtitle = QLabel("Windows endpoint security assessment  \u00b7  Collect, analyze & report")
        subtitle.setObjectName("appSubtitle")
        subtitle.setWordWrap(True)

        titles.addWidget(title)
        titles.addWidget(subtitle)
        row.addLayout(titles, 1)

        badge = QLabel("ENDPOINT AUDIT")
        badge.setObjectName("versionBadge")
        row.addWidget(badge, 0, Qt.AlignTop)

        layout.addLayout(row)
        return header

    def build_header_accent(self):
        """Thin gradient bar that separates the banner from the content."""
        accent = QFrame()
        accent.setObjectName("headerAccent")
        accent.setFixedHeight(3)
        return accent

    def build_body(self):
        """Scrollable content area holding the form cards."""
        scroll = QScrollArea()
        scroll.setObjectName("bodyScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 22, 28, 22)
        layout.setSpacing(16)

        # Inline validation message
        self.error_banner = QLabel()
        self.error_banner.setObjectName("errorBanner")
        self.error_banner.setWordWrap(True)
        self.error_banner.hide()
        layout.addWidget(self.error_banner)

        layout.addWidget(self.build_employee_card())
        layout.addWidget(self.build_coverage_card())
        layout.addStretch(1)

        scroll.setWidget(content)
        return scroll

    def build_employee_card(self):
        """Card with the auditor / subject identity fields."""
        card = Card(
            "Employee Information",
            "This identity is stamped on the header of every generated report.",
        )

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
        self.company_email_input.setPlaceholderText("name@company.com")

        self.date_hired_input = QDateEdit()
        self.date_hired_input.setCalendarPopup(True)
        self.date_hired_input.setDate(QDate.currentDate())
        self.date_hired_input.setDisplayFormat("yyyy-MM-dd")

        self.department_input = QComboBox()
        self.department_input.addItems(["IT", "Security", "Human Resources", "Finance",
                                        "Operations", "Marketing", "Sales"])

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(14)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        grid.addWidget(self.make_field("First Name", self.firstname_input, True), 0, 0)
        grid.addWidget(self.make_field("Last Name", self.lastname_input, True), 0, 1)
        grid.addWidget(self.make_field("Position", self.position_input, True), 1, 0)
        grid.addWidget(self.make_field("Company ID", self.company_id_input, True), 1, 1)
        grid.addWidget(self.make_field("Company Email", self.company_email_input, True), 2, 0)
        grid.addWidget(self.make_field("Department", self.department_input), 2, 1)
        grid.addWidget(self.make_field("Date Hired", self.date_hired_input), 3, 0, 1, 2)

        card.body.addLayout(grid)
        return card

    def build_coverage_card(self):
        """Card listing what the audit collects."""
        card = Card(
            "Audit Coverage",
            "Twelve read-only collectors feed a formatted Excel report with a dashboard.",
        )

        chips = QGridLayout()
        chips.setContentsMargins(0, 0, 0, 0)
        chips.setHorizontalSpacing(8)
        chips.setVerticalSpacing(8)

        for index, name in enumerate(AUDIT_COVERAGE):
            chip = QLabel(name)
            chip.setObjectName("chip")
            chip.setAlignment(Qt.AlignCenter)
            chips.addWidget(chip, index // 3, index % 3)
        for column in range(3):
            chips.setColumnStretch(column, 1)

        card.body.addLayout(chips)

        foot = QLabel("Output format:  Excel (.xlsx)  \u00b7  15 worksheets  \u00b7  Saved to /reports")
        foot.setObjectName("chipMuted")
        foot.setAlignment(Qt.AlignCenter)
        foot.setWordWrap(True)
        card.body.addWidget(foot)

        return card

    def build_footer(self):
        """Sticky action bar."""
        footer = QWidget()
        footer.setObjectName("footer")

        layout = QHBoxLayout(footer)
        layout.setContentsMargins(28, 14, 28, 16)
        layout.setSpacing(12)

        hint = QLabel("Fields marked * are required.")
        hint.setObjectName("chipMuted")
        hint.setWordWrap(True)
        layout.addWidget(hint, 1)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setObjectName("ghostButton")
        self.reset_button.setCursor(Qt.PointingHandCursor)
        self.reset_button.clicked.connect(self.reset_form)
        layout.addWidget(self.reset_button, 0, Qt.AlignVCenter)

        self.submit_button = QPushButton("Start Security Audit")
        self.submit_button.setObjectName("primaryButton")
        self.submit_button.setMinimumWidth(220)
        self.submit_button.setCursor(Qt.PointingHandCursor)
        self.submit_button.clicked.connect(self.start_security_audit)
        layout.addWidget(self.submit_button, 0, Qt.AlignVCenter)

        return footer

    @staticmethod
    def make_field(text, widget, required=False):
        """Stack a caption above an input widget."""
        caption = f"{text} <span style='color:#DC2626; font-weight:700;'>*</span>" if required else text
        label = QLabel(caption)
        label.setObjectName("fieldLabel")
        label.setTextFormat(Qt.RichText)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(label)
        layout.addWidget(widget)
        return container

    # ------------------------------------------------------------------
    # Styling
    # ------------------------------------------------------------------
    def load_stylesheet(self):
        """Load external QSS stylesheet for consistent theming."""
        if not STYLES_PATH.exists():
            print("Warning: styles.qss file not found!")
            return

        stylesheet = STYLES_PATH.read_text(encoding="utf-8")

        # Resolve "url(assets/<file>)" tokens to absolute paths so the theme
        # renders correctly no matter which directory the app is launched from.
        def resolve(match):
            path = (BASE_DIR / match.group(1)).resolve()
            return f"url({QUrl.fromLocalFile(str(path)).toString()})"

        stylesheet = re.sub(r"url\((assets/[^)]+)\)", resolve, stylesheet)
        self.setStyleSheet(stylesheet)

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------
    def required_fields(self):
        """Form fields that must be filled before an audit can start."""
        return [
            (self.firstname_input, "First Name"),
            (self.lastname_input, "Last Name"),
            (self.position_input, "Position"),
            (self.company_id_input, "Company ID"),
            (self.company_email_input, "Company Email"),
        ]

    def set_field_error(self, widget, has_error):
        """Toggle the red error state on an input."""
        widget.setProperty("state", "error" if has_error else "normal")
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def clear_validation(self):
        """Remove all error styling and hide the banner."""
        for widget, _ in self.required_fields():
            self.set_field_error(widget, False)
        self.error_banner.hide()

    def validate_inputs(self):
        """Check that all required fields are filled before starting audit."""
        empty = [name for widget, name in self.required_fields() if not widget.text().strip()]

        for widget, name in self.required_fields():
            self.set_field_error(widget, name in empty)

        if empty:
            missing = ", ".join(empty)
            self.error_banner.setText(
                f"Complete the required fields to continue: {missing}"
                if len(empty) == 1 else
                f"Complete {len(empty)} required fields to continue: {missing}"
            )
            self.error_banner.show()

            first_empty = next(w for w, n in self.required_fields() if n in empty)
            first_empty.setFocus()
            return False

        self.error_banner.hide()
        return True

    def reset_form(self):
        """Clear every input and dismiss validation feedback."""
        self.firstname_input.clear()
        self.lastname_input.clear()
        self.position_input.clear()
        self.company_id_input.clear()
        self.company_email_input.clear()
        self.date_hired_input.setDate(QDate.currentDate())
        self.department_input.setCurrentIndex(0)
        self.clear_validation()
        self.firstname_input.setFocus()

    def start_security_audit(self):
        """Validate inputs, show loading dialog, and start background audit worker."""
        if not self.validate_inputs():
            return

        # Read the form on the GUI thread so the worker never touches widgets
        employee_data = SecurityAudit.get_form_data(self)

        # Show loading dialog (application modal, so the form cannot be edited)
        self.loading = LoadingDialog(self)
        self.loading.show()

        # Create and start background worker
        self.worker = AuditWorker(employee_data)
        self.worker.progress.connect(self.loading.set_progress)
        self.worker.finished.connect(self.on_audit_finished)
        self.worker.error.connect(self.on_audit_error)
        self.worker.start()

    def on_audit_finished(self, filepath):
        """Handle successful completion of the audit."""
        self.loading.close()
        self.loading.deleteLater()   # stops the GIF animation

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Audit complete")
        msg.setText("Security audit finished successfully.")
        msg.setInformativeText(f"15 worksheets were written to:\n{filepath}")

        open_btn = msg.addButton("Open Report", QMessageBox.ActionRole)
        folder_btn = msg.addButton("Open Folder", QMessageBox.ActionRole)
        msg.addButton("Close", QMessageBox.AcceptRole)
        msg.setDefaultButton(open_btn)

        msg.exec()

        # Open the generated report if user clicks the button
        clicked = msg.clickedButton()
        if clicked == open_btn:
            self.open_path(filepath)
        elif clicked == folder_btn:
            self.open_path(str(Path(filepath).parent))

    def on_audit_error(self, error_msg):
        """Handle errors during the audit process."""
        self.loading.close()
        self.loading.deleteLater()   # stops the GIF animation
        QMessageBox.critical(self, "Audit failed",
                             f"Failed to generate report:\n{error_msg}")

    @staticmethod
    def open_path(target):
        """Open a file or folder with the OS default handler."""
        try:
            os.startfile(target)
        except Exception:
            webbrowser.open(QUrl.fromLocalFile(target).toString())


if __name__ == "__main__":
    # Standard PySide6 application entry point
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
