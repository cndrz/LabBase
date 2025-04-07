from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QFormLayout, QMessageBox, QVBoxLayout
from datetime import datetime
import uuid
from request_manager import add_request
from nlp_utils import categorize_request

class UserForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Service Request Form")
        self.setGeometry(100, 100, 600, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #1c1c1c;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QLineEdit, QTextEdit {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 10px;
                padding: 10px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3a86ff;
                border-radius: 10px;
                padding: 10px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005fdd;
            }
            QLabel {
                font-weight: bold;
                font-size: 15px;
                padding: 5px 0;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()
        self.name_input = QLineEdit()
        self.dept_input = QLineEdit()
        self.equip_input = QLineEdit()
        self.desc_input = QTextEdit()
        self.submit_btn = QPushButton("Submit Request")
        self.submit_btn.clicked.connect(self.submit_request)
        form.addRow("Name:", self.name_input)
        form.addRow("Department:", self.dept_input)
        form.addRow("Equipment:", self.equip_input)
        form.addRow("Description:", self.desc_input)
        layout.addLayout(form)
        layout.addWidget(self.submit_btn)
        self.setLayout(layout)

    def submit_request(self):
        name = self.name_input.text()
        dept = self.dept_input.text()
        equip = self.equip_input.text()
        desc = self.desc_input.toPlainText()
        if not desc:
            QMessageBox.warning(self, "Incomplete", "Description is required.")
            return
        request = {
            "id": str(uuid.uuid4())[:8],
            "name": name or "Not mentioned",
            "department": dept or "Not mentioned",
            "equipment": equip or "Not mentioned",
            "description": desc,
            "summary": "",
            "category": categorize_request(desc),
            "status": "Pending",
            "timestamp": datetime.now().isoformat()
        }
        add_request(request)
        QMessageBox.information(self, "Submitted", "Your request has been submitted.")
        self.name_input.clear()
        self.dept_input.clear()
        self.equip_input.clear()
        self.desc_input.clear()
