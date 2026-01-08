import sys
import time
import serial
import os
import csv
import subprocess
from datetime import datetime
import mysql.connector

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer11
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QFrame
)

# ---------------- CONSTANTS ----------------
DEFAULT_PHOTO = r"C:\Users\johnk\Downloads\default_photo.jfif"
HISTORY_DIR = r"C:\Users\johnk\OneDrive\Desktop\Tapping\RFIDsystem\thesis1\tapping\history log"

# ---------------- SERIAL THREAD ----------------
class SerialThread(QThread):
    uid_scanned = pyqtSignal(str)

    def __init__(self, port="COM4", baud=9600):
        super().__init__()
        self.port = port
        self.baud = baud
        self.running = True

    def run(self):
        try:
            ser = serial.Serial(self.port, self.baud, timeout=1)
            time.sleep(2)
            while self.running:
                if ser.in_waiting:
                    uid = ser.readline().decode(errors="ignore").strip()
                    uid = uid.split(":")[-1].strip()
                    self.uid_scanned.emit(uid)
        except Exception as e:
            print("Serial error:", e)

# ---------------- MAIN WINDOW ----------------
class RFIDTapping(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("RFID Fetcher - Student System")
        self.setGeometry(100, 100, 1300, 780)

        self.fetcher_data = None
        self.student_data = None

        # ---------------- DATABASE ----------------
        self.db = self.connect_db()
        self.cursor = self.db.cursor(dictionary=True)

        # ---------------- HISTORY ----------------
        self.history_file = self.get_history_file()
        self.init_history_file()

        # ---------------- UI ----------------
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        left_layout = QHBoxLayout()
        self.fetcher_panel = self.create_person_panel("FETCHER", "#1e3a8a")
        self.student_panel = self.create_person_panel("STUDENT", "#047857")
        left_layout.addWidget(self.fetcher_panel)
        left_layout.addWidget(self.student_panel)

        right_layout = QVBoxLayout()

        title = QLabel("RFID Fetcher - Student System")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("background:#047857;color:white;padding:12px;")
        right_layout.addWidget(title)

        self.status_label = QLabel("WAITING FOR RFID...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.status_label.setStyleSheet("background:#6b7280;color:white;padding:10px;")
        right_layout.addWidget(self.status_label)

        self.open_history_btn = QPushButton("📂 Open History File")
        self.open_history_btn.clicked.connect(self.open_history_file)
        right_layout.addWidget(self.open_history_btn)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Fetcher", "Student", "Date", "Time", "Status"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_layout.addWidget(self.table)

        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 1)

        # ---------------- SERIAL ----------------
        self.serial_thread = SerialThread("COM4")
        self.serial_thread.uid_scanned.connect(self.process_rfid)
        self.serial_thread.start()

        self.pairing_timer = QTimer()
        self.pairing_timer.setSingleShot(True)
        self.pairing_timer.timeout.connect(self.pairing_timeout)

        self.reset_system()

    # ---------------- DATABASE ----------------
    def connect_db(self):
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456",
            database="rfid_system"
        )

    # ---------------- HISTORY ----------------
    def get_history_file(self):
        os.makedirs(HISTORY_DIR, exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(HISTORY_DIR, f"history_{today}.csv")

    def init_history_file(self):
        if not os.path.exists(self.history_file):
            with open(self.history_file, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["Date", "Time", "Fetcher", "Student", "Status"])

    def save_history(self, fetcher, student, status):
        now = datetime.now()
        with open(self.history_file, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                now.strftime("%Y-%m-%d"),
                now.strftime("%H:%M:%S"),
                fetcher, student, status
            ])

    def open_history_file(self):
        subprocess.Popen(["explorer", os.path.abspath(self.history_file)])

    # ---------------- UI HELPERS ----------------
    def create_person_panel(self, title, color):
        frame = QFrame()
        layout = QVBoxLayout(frame)

        lbl = QLabel(title)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
        lbl.setStyleSheet(f"background:{color};color:white;padding:8px;")
        layout.addWidget(lbl)

        img = QLabel()
        img.setAlignment(Qt.AlignCenter)
        layout.addWidget(img)

        name = QLabel("WAITING")
        name.setAlignment(Qt.AlignCenter)
        name.setFont(QFont("Segoe UI", 15, QFont.Bold))
        layout.addWidget(name)

        info = QLabel("")
        info.setAlignment(Qt.AlignCenter)
        info.setFont(QFont("Segoe UI", 13))
        info.setWordWrap(True)
        layout.addWidget(info)

        frame.image = img
        frame.name = name
        frame.info = info
        return frame

    def load_photo(self, path):
        pix = QPixmap(path) if path else QPixmap()
        if pix.isNull():
            pix = QPixmap(DEFAULT_PHOTO)
        return pix.scaled(160, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    # ---------------- RFID LOGIC ----------------
    def process_rfid(self, uid):
        if self.fetcher_data and self.student_data:
            return

        # Try fetcher
        self.cursor.execute("SELECT * FROM fetcher WHERE rfid=%s", (uid,))
        fetcher = self.cursor.fetchone()

        # Try student
        self.cursor.execute("SELECT * FROM student WHERE Student_id=%s", (uid,))
        student = self.cursor.fetchone()

        if fetcher and not self.fetcher_data:
            self.fetcher_data = fetcher
            self.fetcher_panel.image.setPixmap(self.load_photo(fetcher["photo_path"]))
            self.fetcher_panel.name.setText(fetcher["Fetcher_name"])
            self.status_label.setText("FETCHER SCANNED – WAITING FOR STUDENT")
            self.pairing_timer.start(10000)

        elif student and not self.student_data:
            self.student_data = student
            self.student_panel.image.setPixmap(self.load_photo(student["photo_path"]))
            self.student_panel.name.setText(student["Student_name"])
            self.student_panel.info.setText(
                f"Student ID: {student['Student_id']}\n\n"
                f"Grade Level: {student['grade_lvl']}\n\n"
                f"Teacher: {student['Teacher_name']}"
            )
            self.status_label.setText("STUDENT SCANNED – WAITING FOR FETCHER")
            self.pairing_timer.start(10000)

        if self.fetcher_data and self.student_data:
            self.pairing_timer.stop()
            self.verify_pair()

    # ---------------- VERIFY ----------------
    def verify_pair(self):
        self.cursor.execute("""
            SELECT * FROM registrations
            WHERE rfid=%s AND student_id=%s
        """, (
            self.fetcher_data["rfid"],
            self.student_data["Student_id"]
        ))

        verified = self.cursor.fetchone()
        status = "AUTHORIZED" if verified else "DENIED"

        self.finish_pairing(
            status,
            self.fetcher_data["Fetcher_name"],
            self.student_data["Student_name"]
        )

    # ---------------- FINISH ----------------
    def finish_pairing(self, status, fetcher, student):
        now = datetime.now()
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(fetcher))
        self.table.setItem(row, 1, QTableWidgetItem(student))
        self.table.setItem(row, 2, QTableWidgetItem(now.strftime("%Y-%m-%d")))
        self.table.setItem(row, 3, QTableWidgetItem(now.strftime("%H:%M:%S")))
        self.table.setItem(row, 4, QTableWidgetItem(status))

        self.save_history(fetcher, student, status)

        self.status_label.setText(status)
        self.status_label.setStyleSheet(
            f"background:{'#16a34a' if status=='AUTHORIZED' else '#dc2626'};color:white;padding:10px;"
        )

        QTimer.singleShot(3000, self.reset_system)

    # ---------------- RESET ----------------
    def reset_system(self):
        self.fetcher_data = None
        self.student_data = None

        default_pix = self.load_photo(DEFAULT_PHOTO)
        for panel in (self.fetcher_panel, self.student_panel):
            panel.image.setPixmap(default_pix)
            panel.name.setText("WAITING...")
            panel.info.setText("")

        self.status_label.setText("WAITING FOR RFID...")
        self.status_label.setStyleSheet("background:#6b7280;color:white;padding:10px;")

    def pairing_timeout(self):
        self.finish_pairing("DENIED", "UNKNOWN", "NO PAIR")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RFIDTapping()
    window.show()
    sys.exit(app.exec_())
