import sys
import time
import serial
from datetime import datetime
import mysql.connector

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QFrame
)

# ---------------- CONSTANTS ----------------
DEFAULT_PHOTO = r"C:\Users\johnk\Downloads\default_photo.jfif" #ibahin mo nalang yung file path ng default photo pati yung nasa database hardcoded lang yun nasa database

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
        self.setGeometry(100, 100, 1250, 750)

        self.stage = "fetcher"
        self.fetcher_rfid = None
        self.student_rfid = None

        # ---------------- DATABASE ----------------
        self.db = self.connect_db()
        self.cursor = self.db.cursor(dictionary=True)

        # ---------------- UI ----------------
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # -------- LEFT SIDE --------
        left_layout = QHBoxLayout()
        self.fetcher_panel = self.create_person_panel("Fetcher", "#1e3a8a")
        self.student_panel = self.create_person_panel("Student", "#047857")
        left_layout.addWidget(self.fetcher_panel)
        left_layout.addWidget(self.student_panel)

        # -------- RIGHT SIDE --------
        right_layout = QVBoxLayout()

        title = QLabel("RFID Fetcher - Student System")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("background:#047857;color:white;padding:12px;")
        right_layout.addWidget(title)

        self.status_label = QLabel("WAITING FOR RFID")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.status_label.setStyleSheet("background:#6b7280;color:white;padding:10px;")
        right_layout.addWidget(self.status_label)

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

        self.reset_system()

    # ---------------- DATABASE ----------------
    def connect_db(self):
        try:
            return mysql.connector.connect(
                host="localhost",
                user="root",
                password="123456",
                database="rfid_system"
            )
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", str(err))
            sys.exit()

    # ---------------- PERSON PANEL ----------------
    def create_person_panel(self, title, color):
        frame = QFrame()
        layout = QVBoxLayout(frame)

        lbl = QLabel(title)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        lbl.setStyleSheet(f"background:{color};color:white;padding:6px;")
        layout.addWidget(lbl)

        img = QLabel()
        img.setAlignment(Qt.AlignCenter)
        layout.addWidget(img)

        name = QLabel("WAITING")
        name.setAlignment(Qt.AlignCenter)
        name.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(name)

        info = QLabel("")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

        frame.image = img
        frame.name = name
        frame.info = info
        return frame

    # ---------------- PHOTO LOADER ----------------
    def load_photo(self, path):
        pix = QPixmap(path) if path else QPixmap()
        if pix.isNull():
            pix = QPixmap(DEFAULT_PHOTO)
        return pix.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    # ---------------- RFID PROCESS ----------------
    def process_rfid(self, uid):
        if self.stage == "fetcher":
            self.fetcher_rfid = uid
            self.cursor.execute("SELECT * FROM fetcher WHERE rfid=%s", (uid,))
            self.fetcher_data = self.cursor.fetchone()

            if not self.fetcher_data:
                self.set_status("DENIED", "#dc2626")
                QTimer.singleShot(3000, self.reset_system)
                return

            self.update_fetcher_panel()
            self.stage = "student"

        else:
            self.student_rfid = uid
            self.cursor.execute(
                "SELECT * FROM student WHERE Student_id=%s", (uid,)
            )
            self.student_data = self.cursor.fetchone()

            if not self.student_data:
                self.set_status("DENIED", "#dc2626")
                QTimer.singleShot(3000, self.reset_system)
                return

            self.update_student_panel()
            self.verify_pair()

    # ---------------- VERIFY PAIR ----------------
    def verify_pair(self):
        self.cursor.execute("""
            SELECT * FROM registrations
            WHERE rfid = %s
              AND student_id = %s
        """, (self.fetcher_rfid, self.student_data["Student_id"]))

        verified = self.cursor.fetchone()
        now = datetime.now()

        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(self.fetcher_data["Fetcher_name"]))
        self.table.setItem(row, 1, QTableWidgetItem(self.student_data["Student_name"]))
        self.table.setItem(row, 2, QTableWidgetItem(now.strftime("%Y-%m-%d")))
        self.table.setItem(row, 3, QTableWidgetItem(now.strftime("%H:%M:%S")))
        self.table.setItem(row, 4, QTableWidgetItem(
            "AUTHORIZED" if verified else "DENIED"
        ))

        self.set_status(
            "AUTHORIZED" if verified else "DENIED",
            "#16a34a" if verified else "#dc2626"
        )

        QTimer.singleShot(3000, self.reset_system)

    # ---------------- UI UPDATES ----------------
    def update_fetcher_panel(self):
        self.fetcher_panel.image.setPixmap(
            self.load_photo(self.fetcher_data.get("photo_path"))
        )
        self.fetcher_panel.name.setText(self.fetcher_data["Fetcher_name"])

    def update_student_panel(self):
        self.student_panel.image.setPixmap(
            self.load_photo(self.student_data.get("photo_path"))
        )
        self.student_panel.name.setText(self.student_data["Student_name"])
        self.student_panel.info.setText(
            f"Grade Level: {self.student_data['grade_lvl']}\n"
            f"Teacher: {self.student_data['Teacher_name']}\n"
            f"Student ID: {self.student_data['Student_id']}"
        )

    def set_status(self, text, color):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(
            f"background:{color};color:white;padding:10px;"
        )

    # ---------------- RESET ----------------
    def reset_system(self):
        self.stage = "fetcher"
        self.fetcher_rfid = None
        self.student_rfid = None

        default_pix = self.load_photo(DEFAULT_PHOTO)

        for panel in (self.fetcher_panel, self.student_panel):
            panel.image.setPixmap(default_pix)
            panel.name.setText("WAITING...")
            panel.info.setText("")

        self.set_status("WAITING FOR RFID...", "#6b7280")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RFIDTapping()
    window.show()
    sys.exit(app.exec_())
