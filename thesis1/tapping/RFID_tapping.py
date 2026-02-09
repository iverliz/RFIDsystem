import sys, os, mysql.connector, re
from datetime import datetime
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import QUrl, Qt, QTimer 
from PyQt5.QtGui import QPixmap, QFont, QImage
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, 
    QVBoxLayout, QHBoxLayout, QFrame
)

# ================= PATH SETUP =================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from tapping.comms_serial import SerialThread

# ---------------- CONFIG ----------------
ASSETS_DIR = os.path.join(CURRENT_DIR, "assets")
SOUND_DIR = os.path.join(CURRENT_DIR, "sound_effect")
DEFAULT_PHOTO = os.path.join(ASSETS_DIR, "default.png")

class RFIDTapping(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RFID Student Fetcher System - Privacy Protected")
        self.setGeometry(100, 100, 1300, 800)

        try:
            self.db = mysql.connector.connect(
                host="localhost", 
                user="root", 
                password="johnjohn6581506", 
                database="rfid_system"
            )
            self.cursor = self.db.cursor(dictionary=True)
        except Exception as e:
            print(f"Database Connection Error: {e}")
            sys.exit(1)

        self.active_fetcher = None
        self.active_teacher = None
        
        self.init_ui()
        self.init_audio()
        self.init_timers()

        try:
            self.serial = SerialThread(port="COM3", baud=9600)
            self.serial.uid_scanned.connect(self.process_rfid)
            self.serial.start()
        except Exception as e:
            print(f"Serial Error: {e}")

        self.reset_all()

    def mask_name(self, name):
        """Converts 'John Doe' to 'J*** D**' for privacy."""
        if not name: return "N/A"
        parts = name.split()
        masked_parts = []
        for p in parts:
            if len(p) > 1:
                masked_parts.append(p[0] + "*" * (len(p) - 1))
            else:
                masked_parts.append(p)
        return " ".join(masked_parts)

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        self.fetcher_panel = self.create_panel("FETCHER / TEACHER", "#1e3a8a")
        self.student_panel = self.create_panel("STUDENT", "#047857")
        
        left_layout = QHBoxLayout()
        left_layout.addWidget(self.fetcher_panel)
        left_layout.addWidget(self.student_panel)

        right_layout = QVBoxLayout()
        self.title = QLabel("LIVE MONITORING", alignment=Qt.AlignCenter)
        self.title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.title.setStyleSheet("background: #2563eb; color: white; padding: 15px; border-radius: 5px;")

        self.time_label = QLabel(alignment=Qt.AlignCenter)
        self.time_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        
        self.status = QLabel("WAITING FOR SCAN...", alignment=Qt.AlignCenter)
        self.status.setWordWrap(True)
        self.status.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.status.setStyleSheet("background: #6b7280; color: white; padding: 20px; border-radius: 10px;")

        right_layout.addWidget(self.title)
        right_layout.addWidget(self.time_label)
        right_layout.addWidget(self.status)
        right_layout.addStretch()

        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 1)

    def create_panel(self, title, color):
        frame = QFrame()
        frame.setStyleSheet(f"background: white; border: 2px solid {color}; border-radius: 15px;")
        layout = QVBoxLayout(frame)
        header = QLabel(title, alignment=Qt.AlignCenter)
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setStyleSheet(f"background: {color}; color: white; padding: 10px;")
        img = QLabel(alignment=Qt.AlignCenter)
        img.setFixedSize(250, 250)
        img.setScaledContents(True)
        name = QLabel("WAITING...", alignment=Qt.AlignCenter)
        name.setFont(QFont("Segoe UI", 16, QFont.Bold))
        info = QLabel("", alignment=Qt.AlignCenter)
        info.setFont(QFont("Segoe UI", 12))
        info.setWordWrap(True)

        layout.addWidget(header)
        layout.addWidget(img, 0, Qt.AlignCenter)
        layout.addWidget(name)
        layout.addWidget(info)
        layout.addStretch()
        
        frame.header, frame.image, frame.name, frame.info = header, img, name, info
        return frame

    def init_audio(self):
        self.snd_auth = QSoundEffect()
        self.snd_auth.setSource(QUrl.fromLocalFile(os.path.join(SOUND_DIR, "authorized_sound.wav")))
        self.snd_denied = QSoundEffect()
        self.snd_denied.setSource(QUrl.fromLocalFile(os.path.join(SOUND_DIR, "denied_sound.wav")))

    def init_timers(self):
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(lambda: self.time_label.setText(datetime.now().strftime("%I:%M:%S %p")))
        self.clock_timer.start(1000)
        self.reset_timer = QTimer(singleShot=True)
        self.reset_timer.timeout.connect(self.reset_all)

    def process_rfid(self, uid):
        # 1. TEACHER CHECK
        teacher_sql = """
            SELECT t.* FROM teacher t 
            JOIN teacher_rfid_registration tr ON t.teacher_id = tr.employee_id 
            WHERE tr.rfid_uid = %s AND tr.status = 'Active'
        """
        self.cursor.execute(teacher_sql, (uid,))
        teacher = self.cursor.fetchone()
        if teacher:
            self.handle_teacher(teacher)
            return

        # 2. FETCHER CHECK
        self.cursor.execute("SELECT * FROM registrations WHERE rfid=%s AND status='Active'", (uid,))
        fetcher_reg = self.cursor.fetchone()
        if fetcher_reg:
            self.handle_fetcher(fetcher_reg)
            return

        # 3. STUDENT CHECK
        self.cursor.execute("SELECT * FROM registrations WHERE student_rfid=%s AND status='Active'", (uid,))
        student_reg = self.cursor.fetchone()
        if student_reg:
            self.handle_student(student_reg)
            return

        self.status.setText(f"UNKNOWN CARD\n{uid}")
        self.status.setStyleSheet("background: #374151; color: white; padding: 20px;")
        self.snd_denied.play()

    def handle_teacher(self, teacher):
        self.active_teacher = teacher
        self.active_fetcher = None
        self.fetcher_panel.name.setText(f"T. {self.mask_name(teacher['Teacher_name'])}")
        self.fetcher_panel.info.setText(f"Grade Level: {teacher['Teacher_grade']}")
        self.display_photo(self.fetcher_panel.image, teacher.get('photo_path'))
        self.status.setText("TEACHER VERIFIED\nWAITING FOR STUDENT...")
        self.status.setStyleSheet("background: #7c3aed; color: white; padding: 20px;")
        self.snd_auth.play()

    def handle_fetcher(self, reg):
        self.active_fetcher = reg
        self.active_teacher = None
        self.fetcher_panel.name.setText(self.mask_name(reg['fetcher_name']))
        
        self.cursor.execute("SELECT student_name FROM registrations WHERE rfid=%s", (reg['rfid'],))
        siblings = self.cursor.fetchall()
        names = "\n".join([f"• {self.mask_name(s['student_name'])}" for s in siblings])
        
        self.fetcher_panel.info.setText(f"Authorized For:\n{names}")
        self.display_photo(self.fetcher_panel.image, reg.get('photo_path'))
        self.status.setText("FETCHER VERIFIED\nSCAN STUDENT NOW")
        self.status.setStyleSheet("background: #1e3a8a; color: white; padding: 20px;")
        self.snd_auth.play()

    def handle_student(self, student_reg):
        self.student_panel.name.setText(self.mask_name(student_reg['student_name']))
        
        # Display Student Details (Masked for Privacy)
        display_info = (
            f"Grade: {student_reg['grade']}\n"
            f"Teacher: {self.mask_name(student_reg['teacher'])}\n"
            f"Fetcher: {self.mask_name(student_reg['fetcher_name'])}"
        )
        self.student_panel.info.setText(display_info)
        self.display_photo(self.student_panel.image, student_reg.get('photo_path'))
        
        authorized = False
        if self.active_teacher:
            if student_reg['teacher'] == self.active_teacher['Teacher_name']:
                authorized = True
        elif self.active_fetcher:
            if student_reg['rfid'] == self.active_fetcher['rfid']:
                authorized = True

        if authorized:
            self.status.setText("MATCH FOUND: SUCCESS")
            self.status.setStyleSheet("background: #16a34a; color: white; padding: 20px;")
            self.serial.write("AUTHORIZED")
            self.snd_auth.play()
            self.save_log(student_reg)
        else:
            self.status.setText("UNAUTHORIZED PAIRING")
            self.status.setStyleSheet("background: #dc2626; color: white; padding: 20px;")
            self.serial.write("DENIED")
            self.snd_denied.play()
        
        self.reset_timer.start(5000)

    def display_photo(self, label, blob):
        if blob:
            image = QImage.fromData(blob)
            label.setPixmap(QPixmap.fromImage(image))
        else:
            if os.path.exists(DEFAULT_PHOTO):
                label.setPixmap(QPixmap(DEFAULT_PHOTO))

    def save_log(self, reg):
        try:
            issuer = self.active_teacher['Teacher_name'] if self.active_teacher else reg['fetcher_name']
            sql = "INSERT INTO history_log (fetcher_name, student_name, time_out) VALUES (%s, %s, %s)"
            self.cursor.execute(sql, (issuer, reg['student_name'], datetime.now()))
            self.db.commit()
        except: pass

    def reset_all(self):
        self.active_fetcher = None
        self.active_teacher = None
        self.fetcher_panel.name.setText("SCAN FETCHER")
        self.fetcher_panel.info.setText("")
        self.student_panel.name.setText("SCAN STUDENT")
        self.student_panel.info.setText("")
        self.display_photo(self.fetcher_panel.image, None)
        self.display_photo(self.student_panel.image, None)
        self.status.setText("SYSTEM READY")
        self.status.setStyleSheet("background: #6b7280; color: white; padding: 20px;")

    def closeEvent(self, event):
        self.serial.stop()
        self.db.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = RFIDTapping()
    win.show()
    sys.exit(app.exec_())