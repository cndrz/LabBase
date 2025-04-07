from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
import sys
from user_form import UserForm
from admin_dashboard import AdminDashboard

class MainLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Service Request System")
        self.setGeometry(200, 200, 400, 250)
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: white;
                font-family: Arial;
            }
            QPushButton {
                background-color: #3a86ff;
                border-radius: 10px;
                padding: 12px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005fdd;
            }
            QLabel {
                font-size: 20px;
                font-weight: bold;
                padding: 20px;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        label = QLabel("Choose your role:")
        label.setAlignment(Qt.AlignCenter)
        user_btn = QPushButton("User Form")
        user_btn.clicked.connect(self.open_user_form)
        admin_btn = QPushButton("Admin Dashboard")
        admin_btn.clicked.connect(self.open_admin_dashboard)
        layout.addWidget(label)
        layout.addWidget(user_btn)
        layout.addWidget(admin_btn)
        self.setLayout(layout)

    def open_user_form(self):
        self.user_window = UserForm()
        self.user_window.show()

    def open_admin_dashboard(self):
        self.admin_window = AdminDashboard()
        self.admin_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = MainLauncher()
    launcher.show()
    sys.exit(app.exec_())
