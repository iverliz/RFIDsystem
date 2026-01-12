import sys, time, os, csv, subprocess, serial
from datetime import datetime, timedelta
import mysql.connector

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy
)

# ---------------- PATHS ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PHOTO = os.path.join(BASE_DIR, "..", "assets", "default_photo.jfif")
HISTORY_DIR = os.path.join(BASE_DIR, "history log")

# ---------------- SERIAL THREAD ----------------
class SerialThread(QThread):
    uid_scanned = pyqtSignal(str)

    def __init__(self, port="COM4", baud=9600):
        super().__init__()
        self.port = port
        self.baud = baud

    def run(self):
        try:
            ser = serial.Serial(self.port, self.baud, timeout=1)
            time.sleep(2)
            while True:
                if ser.in_waiting:
                    uid = ser.readline().decode(errors="ignore").strip()
                    self.uid_scanned.emit(uid.split(":")[-1].strip())
        except Exception as e:
            print("Serial error:", e)

# ---------------- MAIN WINDOW ----------------
class RFIDTapping(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RFID Fetcher - Student System")
        self.setGeometry(100, 100, 1300, 800)

        # ---------------- DATABASE ----------------
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456",
            database="rfid_system"
        )
        self.cursor = self.db.cursor(dictionary=True)

        # ---------------- STATE ----------------
        self.active_fetcher = None
        self.fetcher_students = []
        self.fetched_students = set()
        self.pending_student = None

        # ---------------- HOLDING QUEUE ----------------
        self.holding = {}

        # ---------------- HISTORY ----------------
        os.makedirs(HISTORY_DIR, exist_ok=True)
        self.history_file = os.path.join(
            HISTORY_DIR, f"history_{datetime.now():%Y-%m-%d}.csv"
        )
        if not os.path.exists(self.history_file):
            with open(self.history_file, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(
                    ["Date", "Time", "Fetcher", "Student", "Status"]
                )

        # ---------------- UI ----------------
        self.init_ui()

        # ---------------- TIMERS ----------------
        self.fetcher_timer = QTimer(singleShot=True)
        self.fetcher_timer.timeout.connect(self.move_fetcher_to_holding)

        self.student_display_timer = QTimer(singleShot=True)
        self.student_display_timer.timeout.connect(self.reset_student_panel)

        self.student_wait_timer = QTimer(singleShot=True)
        self.student_wait_timer.timeout.connect(self.student_wait_timeout)

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)

        self.holding_cleanup = QTimer()
        self.holding_cleanup.timeout.connect(self.cleanup_holding)
        self.holding_cleanup.start(60000)

        # ---------------- SERIAL ----------------
        self.serial = SerialThread()
        self.serial.uid_scanned.connect(self.process_rfid)
        self.serial.start()

        self.reset_all()

    # ---------------- UI (UNCHANGED) ----------------
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main = QHBoxLayout(central)

        self.fetcher_panel = self.create_panel("FETCHER", "#1e3a8a")
        self.student_panel = self.create_panel("STUDENT", "#047857")

        left = QHBoxLayout()
        left.addWidget(self.fetcher_panel)
        left.addWidget(self.student_panel)

        right = QVBoxLayout()

        self.title = QLabel("RFID Fetcher - Student System", alignment=Qt.AlignCenter)
        self.title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.title.setStyleSheet("background:#047857;color:white;padding:12px;")

        self.date_label = QLabel(alignment=Qt.AlignCenter)
        self.time_label = QLabel(alignment=Qt.AlignCenter)
        self.date_label.setFont(QFont("Segoe UI", 12))
        self.time_label.setFont(QFont("Segoe UI", 16, QFont.Bold))

        self.status = QLabel("WAITING FOR RFID...", alignment=Qt.AlignCenter)
        self.status.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.status.setStyleSheet("background:#6b7280;color:white;padding:10px;")

        self.open_btn = QPushButton("📂 Open History File")
        self.open_btn.clicked.connect(
            lambda: subprocess.Popen(["explorer", os.path.abspath(self.history_file)])
        )

        self.holding_layout = QVBoxLayout()
        self.spacer = QFrame()
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        for w in (
            self.title, self.date_label, self.time_label,
            self.status, self.open_btn
        ):
            right.addWidget(w)

        right.addLayout(self.holding_layout)
        right.addWidget(self.spacer)

        main.addLayout(left, 2)
        main.addLayout(right, 1)

    def create_panel(self, title, color):
        frame = QFrame()
        layout = QVBoxLayout(frame)

        lbl = QLabel(title, alignment=Qt.AlignCenter)
        lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
        lbl.setStyleSheet(f"background:{color};color:white;padding:8px;")

        img = QLabel(alignment=Qt.AlignCenter)
        name = QLabel("WAITING", alignment=Qt.AlignCenter)
        name.setFont(QFont("Segoe UI", 15, QFont.Bold))

        info = QLabel("", alignment=Qt.AlignCenter)
        info.setWordWrap(True)
        info.setFont(QFont("Segoe UI", 12))

        for w in (lbl, img, name, info):
            layout.addWidget(w)

        frame.image, frame.name, frame.info = img, name, info
        return frame

    # ---------------- PHOTO ----------------
    def load_photo(self, path):
        pix = QPixmap(path) if path and os.path.exists(path) else QPixmap()
        if pix.isNull():
            pix = QPixmap(DEFAULT_PHOTO)
        return pix.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    # ---------------- RFID ----------------
    def process_rfid(self, uid):
        self.cursor.execute("SELECT * FROM student WHERE Student_id=%s", (uid,))
        student = self.cursor.fetchone()

        if student:
            for rfid, h in self.holding.items():
                if student["Student_id"] in h["student_ids"]:
                    self.student_wait_timer.stop()
                    self.activate_fetcher_from_holding(rfid, student)
                    return

        self.cursor.execute("SELECT * FROM fetcher WHERE rfid=%s", (uid,))
        fetcher = self.cursor.fetchone()

        if fetcher:
            self.student_wait_timer.stop()
            self.activate_fetcher(fetcher)
            return

        if student:
            self.handle_student(student)

    # ---------------- STUDENT FIRST ----------------
    def handle_student(self, student):
        if not self.active_fetcher:
            self.pending_student = student

            self.student_panel.image.setPixmap(self.load_photo(student.get("photo_path")))
            self.student_panel.name.setText(student["Student_name"])
            self.student_panel.info.setText(
                f"ID: {student['Student_id']}\n"
                f"Grade: {student['grade_lvl']}\n"
                f"Teacher: {student['Teacher_name']}"
            )

            self.status.setText("STUDENT SCANNED – WAITING FOR FETCHER")

            # ⏱ 7-second waiting window
            self.student_wait_timer.start(7000)
            return

        self.try_pair(student)

    def student_wait_timeout(self):
        self.pending_student = None
        self.reset_student_panel()
        self.status.setText("WAITING FOR RFID...")
        self.status.setStyleSheet("background:#6b7280;color:white;padding:10px;")

    # ---------------- FETCHER ----------------
    def activate_fetcher(self, fetcher):
        if self.active_fetcher:
            return

        self.active_fetcher = fetcher
        self.fetcher_students = self.get_students(fetcher["rfid"])
        self.fetched_students = set()

        self.fetcher_panel.image.setPixmap(self.load_photo(fetcher.get("photo_path")))
        self.fetcher_panel.name.setText(fetcher["Fetcher_name"])
        self.update_fetcher_student_list()

        self.status.setText("FETCHER READY – WAITING FOR STUDENT")

        if self.pending_student:
            student = self.pending_student
            self.pending_student = None
            self.try_pair(student)
            return

        self.fetcher_timer.start(10000)

    def activate_fetcher_from_holding(self, fetcher_rfid, student):
        holding = self.holding[fetcher_rfid]

        self.active_fetcher = holding["fetcher"]
        self.fetcher_students = holding["students"]
        self.fetched_students = holding["fetched"]

        holding["widget"].hide()

        self.fetcher_panel.image.setPixmap(
            self.load_photo(self.active_fetcher.get("photo_path"))
        )
        self.fetcher_panel.name.setText(self.active_fetcher["Fetcher_name"])
        self.update_fetcher_student_list()

        self.try_pair(student)

    # ---------------- PAIRING (UNCHANGED LOGIC) ----------------
    def try_pair(self, student):

        if student["Student_id"] in self.fetched_students:
            self.status.setText("STUDENT HAS ALREADY BEEN FETCHED")
            self.status.setStyleSheet("background:#f59e0b;color:black;padding:10px;")
            QTimer.singleShot(3000, self.reset_status_waiting_student)
            QTimer.singleShot(3000, self.move_fetcher_to_holding)
            return

        self.cursor.execute("""
            SELECT * FROM registrations
            WHERE rfid=%s AND student_id=%s
        """, (
            self.active_fetcher["rfid"],
            student["Student_id"]
        ))

        authorized = self.cursor.fetchone() is not None
        status = "AUTHORIZED" if authorized else "DENIED"

        self.student_panel.image.setPixmap(self.load_photo(student.get("photo_path")))
        self.student_panel.name.setText(student["Student_name"])
        self.student_panel.info.setText(
            f"ID: {student['Student_id']}\n"
            f"Grade: {student['grade_lvl']}\n"
            f"Teacher: {student['Teacher_name']}"
        )

        self.status.setText(status)
        self.status.setStyleSheet(
            f"background:{'#16a34a' if authorized else '#dc2626'};color:white;padding:10px;"
        )

        self.save_history(
            self.active_fetcher["Fetcher_name"],
            student["Student_name"],
            status
        )

        if authorized:
            self.fetched_students.add(student["Student_id"])
            self.update_fetcher_student_list()

            if len(self.fetched_students) == len(self.fetcher_students):
                self.remove_from_holding(self.active_fetcher["rfid"])
                QTimer.singleShot(3000, self.reset_all)
                return

            self.fetcher_timer.start(10000)

        self.student_display_timer.start(3000)

    # ---------------- HOLDING ----------------
    def move_fetcher_to_holding(self):
        if not self.active_fetcher:
            return

        rfid = self.active_fetcher["rfid"]

        box = QFrame()
        v = QVBoxLayout(box)

        img = QLabel(alignment=Qt.AlignCenter)
        img.setPixmap(self.load_photo(self.active_fetcher.get("photo_path")))
        v.addWidget(img)

        name = QLabel(self.active_fetcher["Fetcher_name"], alignment=Qt.AlignCenter)
        name.setFont(QFont("Segoe UI", 12, QFont.Bold))
        v.addWidget(name)

        student_labels = []
        for s in self.fetcher_students:
            lbl = QLabel("• " + s["Student_name"])
            lbl.setStyleSheet(
                "color:green" if s["Student_id"] in self.fetched_students else "color:gray"
            )
            v.addWidget(lbl)
            student_labels.append(lbl)

        self.holding_layout.addWidget(box)

        self.holding[rfid] = {
            "fetcher": self.active_fetcher,
            "students": self.fetcher_students,
            "student_ids": {s["Student_id"] for s in self.fetcher_students},
            "fetched": self.fetched_students,
            "widget": box,
            "labels": student_labels,
            "expires": datetime.now() + timedelta(hours=1)
        }

        self.reset_all()

    def cleanup_holding(self):
        now = datetime.now()
        for rfid in list(self.holding.keys()):
            if self.holding[rfid]["expires"] < now:
                self.remove_from_holding(rfid)

    def remove_from_holding(self, fetcher_rfid):
        if fetcher_rfid in self.holding:
            self.holding[fetcher_rfid]["widget"].deleteLater()
            del self.holding[fetcher_rfid]

    # ---------------- HELPERS ----------------
    def get_students(self, rfid):
        self.cursor.execute("""
            SELECT s.Student_id, s.Student_name
            FROM registrations r
            JOIN student s ON r.student_id = s.Student_id
            WHERE r.rfid=%s
        """, (rfid,))
        return self.cursor.fetchall()

    def update_fetcher_student_list(self):
        html = "<b>Students to fetch:</b><br>"
        for s in self.fetcher_students:
            color = "green" if s["Student_id"] in self.fetched_students else "gray"
            html += f"<span style='color:{color}'>• {s['Student_name']}</span><br>"
        self.fetcher_panel.info.setText(html)

    def reset_status_waiting_student(self):
        if self.active_fetcher:
            self.status.setText("WAITING FOR STUDENT")
            self.status.setStyleSheet("background:#6b7280;color:white;padding:10px;")

    def reset_student_panel(self):
        self.student_panel.image.setPixmap(self.load_photo(None))
        self.student_panel.name.setText("WAITING...")
        self.student_panel.info.setText("")
        self.status.setText("WAITING FOR RFID...")
        self.status.setStyleSheet("background:#6b7280;color:white;padding:10px;")

    def reset_all(self):
        self.active_fetcher = None
        self.fetcher_students = []
        self.fetched_students = set()
        self.pending_student = None

        self.fetcher_panel.image.setPixmap(self.load_photo(None))
        self.fetcher_panel.name.setText("WAITING...")
        self.fetcher_panel.info.setText("")

        self.reset_student_panel()
        self.fetcher_timer.stop()

        self.status.setText("WAITING FOR RFID...")
        self.status.setStyleSheet("background:#6b7280;color:white;padding:10px;")

    def save_history(self, fetcher, student, status):
        with open(self.history_file, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                datetime.now().strftime("%Y-%m-%d"),
                datetime.now().strftime("%H:%M:%S"),
                fetcher, student, status
            ])

    def update_clock(self):
        now = datetime.now()
        self.date_label.setText(now.strftime("%A, %B %d, %Y"))
        self.time_label.setText(now.strftime("%I:%M:%S %p"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RFIDTapping()
    window.show()
    sys.exit(app.exec_())
