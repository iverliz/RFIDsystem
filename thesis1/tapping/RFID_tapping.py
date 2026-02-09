import sys, time, os, subprocess
import serial
import serial.tools.list_ports
from datetime import datetime

# PyQt5 Imports
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import QUrl, Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy
)

# --- 1. Database & Path Setup ---
# This ensures we can find the utils folder even if run from different directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

try:
    from utils.database import db_connect
except ImportError:
    print("CRITICAL: utils.database not found. Check your folder structure.")

# ---------------- PATHS ----------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PHOTO = os.path.join(CURRENT_DIR, "assets", "default_photo.jfif")
SOUND_DIR = os.path.join(CURRENT_DIR, "sound effect")

AUTHORIZED_SOUND = os.path.join(SOUND_DIR, "authorized_sound.wav")
DENIED_SOUND = os.path.join(SOUND_DIR, "denied_sound.wav")

# ---------------- SERIAL THREAD CLASS ----------------
class SerialThread(QThread):
    uid_scanned = pyqtSignal(str)

    def __init__(self, port="COM4", baud=9600):
        super().__init__()
        self.port = port
        self.baud = baud
        self.ser = None
        self._is_running = True

    def run(self):
        """Main loop that listens for serial data."""
        try:
            available_ports = [p.device for p in serial.tools.list_ports.comports()]
            if self.port not in available_ports:
                print(f"Warning: Serial port {self.port} not found. Available: {available_ports}")
            
            # Open serial with a short timeout to prevent UI hanging
            self.ser = serial.Serial(self.port, self.baud, timeout=0.1)
            time.sleep(2) # Arduino boot time
            
            while self._is_running:
                if self.ser and self.ser.is_open and self.ser.in_waiting:
                    try:
                        raw_data = self.ser.readline().decode(errors="ignore").strip()
                        if raw_data:
                            # Standardize UID format (remove "Card UID:" prefix if present)
                            clean_uid = raw_data.split(":")[-1].strip().upper()
                            if clean_uid:
                                self.uid_scanned.emit(clean_uid)
                    except Exception as e:
                        print(f"Data read error: {e}")
                
                self.msleep(50)

        except Exception as e:
            print(f"Serial connection error on {self.port}: {e}")
        finally:
            self.stop()

    def write(self, message):
        """Sends 'A' (Authorized) or 'D' (Denied) to Arduino."""
        if self.ser and self.ser.is_open:
            try:
                self.ser.write((message + "\n").encode())
            except Exception as e:
                print(f"Serial write error: {e}")

    def stop(self):
        self._is_running = False
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except:
                pass
        self.quit()

# ---------------- MAIN WINDOW CLASS ----------------
class RFIDTapping(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RFID Student Fetcher System - Cainta Catholic College")
        self.setGeometry(100, 100, 1300, 800)

        # --- 1. Database Connection ---
        self.db = None
        self.cursor = None
        try:
            self.db = db_connect()
            self.cursor = self.db.cursor(dictionary=True)
            print("Database Connected Successfully.")
        except Exception as e:
            print(f"Database Error: {e}")

        # --- 2. State Variables ---
        self.active_fetcher = None
        self.active_teacher = None
        self.serial = None
        
        # --- 3. UI, Audio & Timers ---
        self.init_ui()
        self.init_timers()
        self.init_audio()
        self.reset_all()

        # --- 4. Serial Hardware Connection ---
        # We start hardware last so the UI is already visible
        self.start_hardware()

    def start_hardware(self):
        available_ports = [p.device for p in serial.tools.list_ports.comports()]
        if not available_ports:
            print("No COM ports detected. Running in OFFLINE MODE.")
            return

        # Attempt to find the RFID Reader on common ports
        for port in ["COM3", "COM4", "COM5"] + available_ports:
            if port in available_ports:
                try:
                    self.serial = SerialThread(port=port, baud=9600)
                    self.serial.uid_scanned.connect(self.process_rfid)
                    self.serial.start()
                    print(f"RFID Reader Connected on {port}.")
                    break 
                except Exception:
                    continue

    def init_timers(self):
        self.student_display_timer = QTimer(singleShot=True)
        self.student_display_timer.timeout.connect(self.reset_student_panel)

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)

    def init_audio(self):
        self.sound_authorized = QSoundEffect()
        self.sound_authorized.setSource(QUrl.fromLocalFile(AUTHORIZED_SOUND))
        self.sound_authorized.setVolume(0.9)

        self.sound_denied = QSoundEffect()
        self.sound_denied.setSource(QUrl.fromLocalFile(DENIED_SOUND))
        self.sound_denied.setVolume(0.9)

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # --- LEFT SIDE: PANELS ---
        self.fetcher_panel = self.create_panel("FETCHER / GUARDIAN", "#1e3a8a")
        self.student_panel = self.create_panel("STUDENT INFO", "#047857")

        left_side = QHBoxLayout()
        left_side.addWidget(self.fetcher_panel)
        left_side.addWidget(self.student_panel)

        # --- RIGHT SIDE: CONTROLS ---
        right_side = QVBoxLayout()

        self.title = QLabel("LIVE MONITORING", alignment=Qt.AlignCenter)
        self.title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.title.setStyleSheet("background: #2563eb; color: white; padding: 12px; border-radius: 5px;")

        self.datetime_frame = QFrame()
        self.datetime_frame.setStyleSheet("background:#d4d4d8; border-radius:10px; padding:10px;")
        dt_layout = QVBoxLayout(self.datetime_frame)
        self.date_label = QLabel(alignment=Qt.AlignCenter)
        self.time_label = QLabel(alignment=Qt.AlignCenter)
        self.date_label.setFont(QFont("Segoe UI", 12))
        self.time_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        dt_layout.addWidget(self.date_label)
        dt_layout.addWidget(self.time_label)

        self.status = QLabel("WAITING FOR SCAN...", alignment=Qt.AlignCenter)
        self.status.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.status.setStyleSheet("background:#6b7280; color:white; padding:20px; border-radius: 5px;")
        self.status.setWordWrap(True)

        self.spacer = QFrame()
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        right_side.addWidget(self.title)
        right_side.addWidget(self.datetime_frame)
        right_side.addWidget(self.status)
        right_side.addWidget(self.spacer)

        main_layout.addLayout(left_side, 2)
        main_layout.addLayout(right_side, 1)

    def create_panel(self, title, color):
        frame = QFrame()
        frame.setStyleSheet(f"background: #f8fafc; border: 3px solid {color}; border-radius: 15px;")
        
        layout = QVBoxLayout(frame)
        lbl = QLabel(title, alignment=Qt.AlignCenter)
        lbl.setFont(QFont("Segoe UI", 18, QFont.Bold))
        lbl.setStyleSheet(f"background:{color}; color:white; padding:10px; border-top-left-radius:10px; border-top-right-radius:10px;")
        
        img = QLabel(alignment=Qt.AlignCenter)
        img.setFixedSize(250, 250)
        img.setStyleSheet("border: 1px solid #cbd5e1; background: white;")
        img.setScaledContents(True)
        img.setPixmap(QPixmap(DEFAULT_PHOTO))
        
        name = QLabel("WAITING...", alignment=Qt.AlignCenter)
        name.setFont(QFont("Segoe UI", 18, QFont.Bold))
        
        info = QLabel("", alignment=Qt.AlignCenter)
        info.setFont(QFont("Segoe UI", 12))
        info.setStyleSheet("color: #475569;")

        layout.addWidget(lbl)
        layout.addWidget(img, 0, Qt.AlignCenter)
        layout.addWidget(name)
        layout.addWidget(info)
        
        frame.image, frame.name, frame.info = img, name, info
        return frame

    def load_photo(self, path):
        if path and os.path.exists(path):
            pix = QPixmap(path)
        else:
            pix = QPixmap(DEFAULT_PHOTO)
        return pix.scaled(250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def process_rfid(self, uid):
        if not self.cursor: return
        
        print(f"DEBUG: Tag Scanned -> {uid}")

        # 1. Check if Teacher (Master Key)
        self.cursor.execute("SELECT * FROM teacher WHERE rfid = %s", (uid,))
        teacher = self.cursor.fetchone()
        if teacher:
            self.active_teacher = teacher
            self.active_fetcher = None 
            self.status.setText(f"TEACHER OVERRIDE ACTIVE\nAuthorized by: {teacher['Teacher_name']}")
            self.status.setStyleSheet("background: #7c3aed; color: white; padding: 15px;")
            self.sound_authorized.play()
            return

        # 2. Check if Fetcher
        self.cursor.execute("SELECT * FROM fetcher WHERE rfid = %s", (uid,))
        fetcher = self.cursor.fetchone()
        if fetcher:
            self.active_fetcher = fetcher
            self.active_teacher = None
            self.update_fetcher_ui(fetcher)
            self.status.setText("FETCHER IDENTIFIED\nREADY TO SCAN STUDENT")
            self.status.setStyleSheet("background: #1e3a8a; color: white; padding: 15px;")
            self.sound_authorized.play()
            return

        # 3. Check if Student
        self.cursor.execute("SELECT * FROM student WHERE student_rfid = %s", (uid,))
        student = self.cursor.fetchone()
        if student:
            self.handle_student_scanned(student)
            return
            
        # 4. Unknown Card
        self.status.setText(f"UNKNOWN TAG DETECTED\nUID: {uid}")
        self.status.setStyleSheet("background: #4b5563; color: white; padding: 15px;")
        self.sound_denied.play()

    def handle_student_scanned(self, student):
        self.update_student_ui(student)
        authorized = False
        authority_name = ""

        # Logic for Teacher Override
        if self.active_teacher:
            authorized = True
            authority_name = f"Teacher Override: {self.active_teacher['Teacher_name']}"
        
        # Logic for Fetcher Pairing
        elif self.active_fetcher:
            authority_name = self.active_fetcher['Fetcher_name']
            # We verify in the registrations table if this RFID is allowed to take THIS specific student
            check_sql = "SELECT * FROM registrations WHERE rfid = %s AND student_id = %s AND status = 'Active'"
            self.cursor.execute(check_sql, (self.active_fetcher['rfid'], student['Student_id']))
            if self.cursor.fetchone():
                authorized = True

        if authorized:
            self.status.setText(f"ACCESS GRANTED\nStudent: {student['Student_name']}")
            self.status.setStyleSheet("background: #16a34a; color: white; padding: 15px;")
            self.sound_authorized.play()
            if self.serial: self.serial.write("A") # Signal Arduino Green LED
            self.save_history_log(student, authority_name)
        else:
            self.status.setText("ACCESS DENIED\nUnauthorized Pairing")
            self.status.setStyleSheet("background: #dc2626; color: white; padding: 15px;")
            self.sound_denied.play()
            if self.serial: self.serial.write("D") # Signal Arduino Red LED

        self.student_display_timer.start(5000)

    def save_history_log(self, student, authority_name):
        try:
            log_sql = """
                INSERT INTO history_log 
                (fetcher_name, student_name, student_id, grade, teacher, location, time_out)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            data = (
                authority_name, 
                student['Student_name'], 
                student['Student_id'], 
                student['grade_lvl'], 
                student['Teacher_name'], 
                "Main Gate", 
                datetime.now()
            )
            self.cursor.execute(log_sql, data)

            # Auto-Cleanup: Deletes logs older than 7 days
            self.cursor.execute("DELETE FROM history_log WHERE time_out < NOW() - INTERVAL 7 DAY")
            self.db.commit()
        except Exception as e:
            print(f"Logging Error: {e}")

    def update_fetcher_ui(self, fetcher):
        self.fetcher_panel.name.setText(fetcher["Fetcher_name"])
        self.fetcher_panel.info.setText(f"ID: {fetcher.get('Fetcher_id', 'N/A')}\nRelation: Authorized")
        
    def update_student_ui(self, student):
        self.student_panel.image.setPixmap(self.load_photo(student.get("photo_path")))
        self.student_panel.name.setText(student["Student_name"])
        self.student_panel.info.setText(f"Grade: {student['grade_lvl']}\nTeacher: {student['Teacher_name']}")

    def update_clock(self):
        now = datetime.now()
        self.date_label.setText(now.strftime("%A, %B %d, %Y"))
        self.time_label.setText(now.strftime("%I:%M:%S %p"))

    def reset_all(self):
        self.active_fetcher = None
        self.active_teacher = None
        self.fetcher_panel.name.setText("WAITING...")
        self.fetcher_panel.info.setText("")
        self.reset_student_panel()

    def reset_student_panel(self):
        self.student_panel.image.setPixmap(QPixmap(DEFAULT_PHOTO))
        self.student_panel.name.setText("WAITING...")
        self.student_panel.info.setText("")

    def closeEvent(self, event):
        if self.serial:
            self.serial.stop()
            self.serial.wait()
        if self.db:
            self.db.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RFIDTapping()
    window.show()
    sys.exit(app.exec_())