import sys
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QTextEdit, QTableWidget, QTableWidgetItem,
    QFileDialog, QStackedLayout
)
from request_manager import load_requests, update_request_status, update_summary
from nlp_utils import summarize_text, extract_keywords, detect_urgency, extract_schedule

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class AdminDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Dashboard")
        self.setGeometry(100, 100, 1200, 700)
        self.requests = load_requests()
        self.filtered_requests = self.requests
        self.selected_id = None

        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: white;
                font-family: 'Segoe UI';
            }
            QPushButton {
                background-color: #3a86ff;
                border-radius: 8px;
                padding: 10px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005fdd;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 6px;
            }
            QTableWidget {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #444;
                border-radius: 6px;
            }
        """)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        sidebar = QVBoxLayout()
        self.stack = QStackedLayout()

        # --- Sidebar buttons ---
        btn_case = QPushButton("📥 Case Manager")
        btn_analytics = QPushButton("📊 Analytics")
        btn_export = QPushButton("📤 Export")

        btn_case.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_analytics.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_export.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        for btn in [btn_case, btn_analytics, btn_export]:
            sidebar.addWidget(btn)
            btn.setMinimumHeight(40)

        main_layout.addLayout(sidebar, 1)

        # --- Stack Views ---
        self.stack.addWidget(self.case_manager_view())
        self.stack.addWidget(self.analytics_view())
        self.stack.addWidget(self.export_view())

        main_layout.addLayout(self.stack, 5)
        self.setLayout(main_layout)

    # --------------------- CASE VIEW ---------------------
    def case_manager_view(self):
        container = QWidget()
        layout = QVBoxLayout()

        # Filters
        filter_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search keyword...")
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Pending", "Accepted", "Completed"])
        self.status_filter.currentIndexChanged.connect(self.apply_filters)
        self.search_input.textChanged.connect(self.apply_filters)

        filter_row.addWidget(QLabel("Search:"))
        filter_row.addWidget(self.search_input)
        filter_row.addWidget(QLabel("Status:"))
        filter_row.addWidget(self.status_filter)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Equipment", "Category", "Status"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(self.display_details)

        # NLP fields
        self.description_box = QTextEdit(); self.description_box.setReadOnly(True)
        self.summary_box = QTextEdit(); self.summary_box.setReadOnly(True)
        self.keywords_box = QTextEdit(); self.keywords_box.setReadOnly(True)
        self.urgency_box = QLineEdit(); self.urgency_box.setReadOnly(True)

        self.status_dropdown = QComboBox()
        self.status_dropdown.addItems(["Pending", "Accepted", "Completed"])
        self.generate_btn = QPushButton("Generate NLP Summary")
        self.generate_btn.clicked.connect(self.generate_nlp)
        self.update_btn = QPushButton("Update Status")
        self.update_btn.clicked.connect(self.update_status)

        layout.addLayout(filter_row)
        layout.addWidget(self.table)
        layout.addWidget(QLabel("Description")); layout.addWidget(self.description_box)
        layout.addWidget(QLabel("Summary")); layout.addWidget(self.summary_box)
        layout.addWidget(self.generate_btn)
        layout.addWidget(QLabel("Keywords")); layout.addWidget(self.keywords_box)
        layout.addWidget(QLabel("Urgency")); layout.addWidget(self.urgency_box)
        layout.addWidget(QLabel("Set Status:")); layout.addWidget(self.status_dropdown)
        layout.addWidget(self.update_btn)

        container.setLayout(layout)
        self.apply_filters()
        return container

    def apply_filters(self):
        text = self.search_input.text().lower()
        status = self.status_filter.currentText()

        def match(req):
            return (
                (text in req["description"].lower() or text in req["equipment"].lower())
                and (status == "All" or req["status"] == status)
            )

        self.filtered_requests = [r for r in self.requests if match(r)]
        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(len(self.filtered_requests))
        for row, req in enumerate(self.filtered_requests):
            self.table.setItem(row, 0, QTableWidgetItem(req["id"]))
            self.table.setItem(row, 1, QTableWidgetItem(req.get("equipment", "")))
            self.table.setItem(row, 2, QTableWidgetItem(req.get("category", "")))
            self.table.setItem(row, 3, QTableWidgetItem(req.get("status", "")))

    def display_details(self, row, _):
        req = self.filtered_requests[row]
        self.selected_id = req["id"]
        self.description_box.setText(req.get("description", ""))
        self.summary_box.setText(req.get("summary", ""))
        self.keywords_box.clear()
        self.urgency_box.clear()

    def generate_nlp(self):
        if not self.selected_id: return
        req = next((r for r in self.requests if r["id"] == self.selected_id), None)
        if not req: return
        summary = summarize_text(req["description"])
        urgency = detect_urgency(req["description"])
        keywords = extract_keywords(req["description"])
        schedule = extract_schedule(req["description"])

        structured = (
            f"- Name: {req.get('name', 'Not mentioned')}\n"
            f"- Department: {req.get('department', 'Not mentioned')}\n"
            f"- Equipment: {req.get('equipment', 'Not mentioned')}\n"
            f"- Category: {req.get('category', 'Uncategorized')}\n"
            f"- Urgency: {urgency}\n"
            f"- Schedule: {schedule or 'Not mentioned'}\n"
            f"- Reason: {summary}\n"
            f"- Keywords: {', '.join(keywords[:5]) if keywords else 'Not detected'}"
        )
        self.summary_box.setText(structured)
        self.keywords_box.setText(", ".join(keywords[:5]) if keywords else "")
        self.urgency_box.setText(urgency)
        update_summary(req["id"], structured)

    def update_status(self):
        if not self.selected_id: return
        update_request_status(self.selected_id, self.status_dropdown.currentText())
        self.requests = load_requests()
        self.apply_filters()

    # --------------------- ANALYTICS VIEW ---------------------
    def analytics_view(self):
        container = QWidget()
        layout = QVBoxLayout()

        category_count = {}
        status_count = {}
        urgency_count = {"High": 0, "Normal": 0}

        for r in self.requests:
            cat = r.get("category", "Uncategorized")
            status = r.get("status", "Pending")
            category_count[cat] = category_count.get(cat, 0) + 1
            status_count[status] = status_count.get(status, 0) + 1
            urgency = detect_urgency(r["description"])
            urgency_count[urgency] += 1

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(category_count.keys(), category_count.values(), label="By Category")
        ax.set_title("Requests by Category")
        ax.set_ylabel("Count")
        layout.addWidget(FigureCanvas(fig))

        fig2, ax2 = plt.subplots(figsize=(8, 4))
        ax2.pie(status_count.values(), labels=status_count.keys(), autopct='%1.1f%%')
        ax2.set_title("Request Status Distribution")
        layout.addWidget(FigureCanvas(fig2))

        fig3, ax3 = plt.subplots(figsize=(5, 4))
        ax3.bar(urgency_count.keys(), urgency_count.values(), color=['red', 'green'])
        ax3.set_title("Urgency Level")
        layout.addWidget(FigureCanvas(fig3))

        container.setLayout(layout)
        return container

    # --------------------- EXPORT VIEW ---------------------
    def export_view(self):
        container = QWidget()
        layout = QVBoxLayout()

        btn_csv = QPushButton("Export All Requests to CSV")
        btn_csv.clicked.connect(self.export_csv)

        btn_pdf = QPushButton("📄 Export (PDF coming soon)")
        btn_pdf.setEnabled(False)  # Placeholder

        layout.addWidget(QLabel("Export Tools"))
        layout.addWidget(btn_csv)
        layout.addWidget(btn_pdf)
        container.setLayout(layout)
        return container

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv)")
        if not path: return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Department", "Equipment", "Status", "Category", "Description", "Summary"])
            for req in self.requests:
                writer.writerow([
                    req["id"], req.get("name", ""), req.get("department", ""), req.get("equipment", ""),
                    req.get("status", ""), req.get("category", ""), req.get("description", ""), req.get("summary", "")
                ])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AdminDashboard()
    win.show()
    sys.exit(app.exec_())
