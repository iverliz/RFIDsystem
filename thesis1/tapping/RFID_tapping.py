import sys, time, os, csv, subprocess, serial
from datetime import datetime, timedelta
import mysql.connector

from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import QUrl, QByteArray

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy
)


# ---------------- PATHS ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PHOTO = os.path.join(BASE_DIR, "..", "assets", "default_photo.jfif")
HISTORY_DIR = os.path.join(BASE_DIR, "history log")

LOGO_PATH = os.path.join(BASE_DIR, "logo", "logo.png")

SOUND_DIR = os.path.join(BASE_DIR, "soundeffect")

AUTHORIZED_SOUND = os.path.join(SOUND_DIR, "authorized.wav")
DENIED_SOUND = os.path.join(SOUND_DIR, "denied.wav")

# ---------------- SERIAL THREAD ----------------
class SerialThread(QThread):
    uid_scanned = pyqtSignal(str)

    def __init__(self, port="COM4", baud=9600):
        super().__init__()
        self.port = port
        self.baud = baud
        self.ser = None

    def run(self):
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=1)
            time.sleep(2)
            while self.isRunning():
                if self.ser.in_waiting:
                    uid = self.ser.readline().decode(errors="ignore").strip()
                    clean_uid = uid.split(":")[-1].strip()
                    self.uid_scanned.emit(clean_uid)
        except Exception as e:
            print("Serial error:", e)

    def write(self, message):
        if self.ser and self.ser.is_open:
            self.ser.write((message + "\n").encode())

    # ---------------- STOP ----------------
    def stop(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
    

# ---------------- MAIN WINDOW ----------------
class RFIDTapping(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RFID Fetcher - Student System")

        if os.path.exists(LOGO_PATH):
            self.setWindowIcon(QIcon(LOGO_PATH))
            
        self.setGeometry(100, 100, 1300, 800)

        # ---------------- DATABASE ----------------
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="123456",
                database="rfid_system"
            )
            self.cursor = self.db.cursor(dictionary=True)
            print("Database connected successfully.")
        except Exception as e:
            print("Database error:", e)
            sys.exit(1)

        # ---------------- STATE ----------------
        self.active_fetcher = None
        self.fetcher_students = []
        self.fetched_students = set()
        self.pending_student = None
        self.completed_fetchers = set()

        self.active_teacher = None
        self.teacher_timer = QTimer(singleShot=True)
        self.teacher_timer.timeout.connect(self.reset_teacher_mode)

        self.globally_fetched_students = set()

        self.student_fetched_by = {}

        self.last_paired_type = None   # "FETCHER" or "TEACHER"
        self.last_paired_data = None   # fetcher or teacher row


        self.replay_mode = False

        

        # ---------------- HOLDING QUEUE ----------------
        self.holding = {}

        self.holding_page_index = 0
        self.holding_cards_per_page = 1

        self.holding_pagination_timer = QTimer()
        self.holding_pagination_timer.timeout.connect(self.rotate_holding_page)
        self.holding_pagination_timer.start(4000)  # change page every 4 seconds

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

        # 🔊 SOUND EFFECTS (ADD THIS BLOCK)
        self.sound_authorized = QSoundEffect()
        self.sound_authorized.setSource(QUrl.fromLocalFile(AUTHORIZED_SOUND))
        self.sound_authorized.setVolume(0.9)

        self.sound_denied = QSoundEffect()
        self.sound_denied.setSource(QUrl.fromLocalFile(DENIED_SOUND))
        self.sound_denied.setVolume(0.9)

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
        self.title.setStyleSheet("""
                        QLabel {
                            color: white;
                            padding: 12px;
                            font-weight: bold;
                            text-shadow: 1px 1px 2px rgba(0,0,0,120);
                            background: qlineargradient(
                                x1:0, y1:0,
                                x2:1, y2:0,
                                stop:0 #2563eb,   /* blue */
                                stop:1 #eab308    /* slightly darker yellow */
                            );
                        }
                    """)

        # ---- DATE & TIME BOX ----
        self.datetime_frame = QFrame()
        self.datetime_frame.setStyleSheet(
            "background:#d4d4d8;border-radius:10px;padding:3px;"
        )

        dt_layout = QVBoxLayout(self.datetime_frame)
        dt_layout.setSpacing(2)

        self.date_label = QLabel(alignment=Qt.AlignCenter)
        self.time_label = QLabel(alignment=Qt.AlignCenter)

        self.date_label.setFont(QFont("Segoe UI", 12))
        self.time_label.setFont(QFont("Segoe UI", 16, QFont.Bold))

        dt_layout.addWidget(self.date_label)
        dt_layout.addWidget(self.time_label)

        self.status = QLabel("WAITING FOR RFID...", alignment=Qt.AlignCenter)
        self.status.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.status.setStyleSheet("background:#6b7280;color:white;padding:10px;")

        self.open_btn = QPushButton("📂 Open History File")
        self.open_btn.setStyleSheet("font-size:10px;padding:3px;")
        self.open_btn.clicked.connect(
            lambda: subprocess.Popen(["explorer", os.path.abspath(self.history_file)])
        )
        
        self.holding_layout = QVBoxLayout()
        self.spacer = QFrame()
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        for w in (
            self.title, self.datetime_frame,
            self.status, self.open_btn, 
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
        lbl.setFont(QFont("Segoe UI", 25, QFont.Bold))
        lbl.setStyleSheet(f"background:{color};color:white;padding:8px;")

        img = QLabel(alignment=Qt.AlignHCenter)
        img.setFixedSize(220, 220)   # 🔥 bigger square
        img.setScaledContents(False)
        img.setContentsMargins(0, 20, 0, 0)
        
        name = QLabel("WAITING", alignment=Qt.AlignCenter)
        name.setFont(QFont("Segoe UI", 17, QFont.Bold))

        info = QLabel("", alignment=Qt.AlignCenter)
        info.setWordWrap(True)
        info.setFont(QFont("Segoe UI", 14))

        layout.addWidget(lbl)
        layout.addWidget(img, alignment=Qt.AlignHCenter)
        layout.addWidget(name)
        layout.addWidget(info)

        frame.title_label = lbl

        frame.image, frame.name, frame.info = img, name, info
        return frame

    # ---------------- PHOTO ----------------
    def load_photo(self, image_data):
        pix = QPixmap()

        if image_data:
            pix.loadFromData(image_data)

        if pix.isNull():
            pix = QPixmap(DEFAULT_PHOTO)

        # 🔥 FORCE SQUARE CROP (CENTER CROP)
        size = min(pix.width(), pix.height())
        x = (pix.width() - size) // 2
        y = (pix.height() - size) // 2

        square = pix.copy(x, y, size, size)

        # 🔥 SCALE BIGGER SQUARE
        return square.scaled(
            160,
            160,
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation
        )
    

    # ---------------- RFID ----------------
    def process_rfid(self, uid):

        # 🔍 CHECK IN REGISTRATIONS TABLE
        self.cursor.execute("""
            SELECT * FROM registrations
            WHERE rfid=%s OR student_rfid=%s
        """, (uid, uid))

        rows = self.cursor.fetchall()

        # -------------------------------------------------
        # 🔵 CHECK IF RFID IS A TEACHER
        # -------------------------------------------------

        self.cursor.execute("""
            SELECT * FROM teacher_rfid_registration
            WHERE rfid_uid=%s
        """, (uid,))

        teacher_reg = self.cursor.fetchone()

        if teacher_reg:

            # 🔒 BLOCK IF TEACHER NOT ACTIVE
            if teacher_reg.get("status") != "Active":

                self.status.setText("TEACHER ACCOUNT IS INACTIVE")
                self.status.setStyleSheet(
                    "background:#dc2626;color:white;padding:10px;"
                )

                QTimer.singleShot(4000, self.reset_status_waiting_rfid)
                return

            employee_id = teacher_reg.get("employee_id")

            if not employee_id:
                return

            # 🔎 GET USERNAME FROM USERS TABLE
            self.cursor.execute("""
                SELECT username FROM users
                WHERE employee_id=%s
            """, (employee_id,))

            user_row = self.cursor.fetchone()

            if not user_row:
                return

            username = user_row.get("username")

            # 🔎 GET TEACHER INFO FROM TEACHER TABLE
            self.cursor.execute("""
                SELECT * FROM teacher
                WHERE teacher_name=%s
            """, (username,))

            teacher_row = self.cursor.fetchone()

            if not teacher_row:
                return

            # BUILD TEACHER OBJECT (COMPATIBLE WITH EXISTING LOGIC)
            teacher = {
                "Teacher_name": teacher_row["teacher_name"],
                "Teacher_grade": teacher_row["teacher_grade"],
                "photo_path": teacher_row["photo_path"]  # BLOB
            }

            self.activate_teacher(teacher)
            return

        if not rows:
            return  # Not registered

        # -------------------------------------------------
        # IF RFID IS A FETCHER (MATCHED IN rfid COLUMN)
        # -------------------------------------------------
        fetcher_rows = [r for r in rows if r["rfid"] == uid]

        if fetcher_rows:
            fetcher_data = fetcher_rows[0]

            # 🚫 BLOCK IF ALL STUDENTS ALREADY FETCHED
            students = self.get_students(uid)

            if not students:
                self.show_temp_status(
                    "FETCHER HAS NO ACTIVE STUDENTS",
                    bg="#dc2626",
                    fg="white",
                    delay=4000
                )
                return
            
            fetched_count = sum(
                1 for s in students
                if s["Student_rfid"] in self.globally_fetched_students
            )

            if students and fetched_count == len(students):
                self.completed_fetchers.add(uid)
                self.show_temp_status(
                    "FETCHER HAS COMPLETED ALL STUDENTS",
                    bg="#334155",
                    fg="white"
                )
                return

            # Build fetcher object (SIMULATE OLD STRUCTURE)
            fetcher = {
                "rfid": uid,
                "Fetcher_name": fetcher_data["fetcher_name"],
                "photo_path": fetcher_data["fetcher_photo_path"]
            }

            if uid in self.completed_fetchers:
                self.show_temp_status(
                    "FETCHER HAS COMPLETED ALL STUDENTS",
                    bg="#334155",
                    fg="white"
                )
                return

            if uid in self.holding and not self.active_fetcher:
                self.show_temp_status(
                    "FETCHER IS ALREADY IN HOLDING QUEUE"
                )
                return

            self.activate_fetcher(fetcher)
            return

        # -------------------------------------------------
        # IF RFID IS A STUDENT (MATCHED IN student_rfid)
        # -------------------------------------------------
        student_rows = [r for r in rows if r["student_rfid"] == uid]

        if student_rows:
            student_data = student_rows[0]

            if student_data.get("status") != "Active":

                self.status.setText("STUDENT ACCOUNT IS INACTIVE")
                self.status.setStyleSheet(
                    "background:#dc2626;color:white;padding:10px;"
                )

                QTimer.singleShot(4000, self.reset_status_waiting_rfid)
                return

            student = {
                "Student_id": student_data["student_id"],  # ✅ real student_id
                "Student_rfid": uid,                      # keep RFID if needed
                "Student_name": student_data["student_name"],
                "grade_lvl": student_data["grade"],
                "Teacher_name": student_data["teacher"],
                "photo_path": student_data["photo_path"],
                "fetcher_name": student_data["fetcher_name"]
            }

            # 🔒 GLOBAL BLOCK
            if student["Student_rfid"] in self.globally_fetched_students:

                if student["Student_rfid"] in self.globally_fetched_students:

                    self.show_temp_status(
                        "STUDENT ALREADY FETCHED – TAP NOT ALLOWED",
                        bg="#334155",
                        fg="white",
                        delay=4000
                    )

                    return

            self.handle_student(student)
            return
            

    # ---------------- STUDENT FIRST ----------------
    def handle_student(self, student):

        if self.active_teacher:

            self.student_panel.image.setPixmap(
            self.load_photo(student.get("photo_path"))
            )
            self.student_panel.name.setText(student["Student_name"])
            self.student_panel.info.setText(
                f"ID: {student['Student_id']}\n"
                f"Grade: {student['grade_lvl']}\n"
                f"Teacher: {student['Teacher_name']}"
            )

            self.try_pair(student)
            return

        if not self.active_fetcher:

            # 🔎 CHECK IF STUDENT BELONGS TO A FETCHER IN HOLDING
            for rfid, h in self.holding.items():
                if student["Student_id"] in h["student_ids"]:

                    # Stop waiting timer if running
                    self.student_wait_timer.stop()

                    # Activate that fetcher from holding and pair
                    self.activate_fetcher_from_holding(rfid, student)
                    return

            # If no matching fetcher found in holding → normal waiting behavior
            self.pending_student = student

            self.student_panel.image.setPixmap(
                self.load_photo(student.get("photo_path"))
            )
            self.student_panel.name.setText(student["Student_name"])
            self.student_panel.info.setText(
                f"ID: {student['Student_id']}\n"
                f"Grade: {student['grade_lvl']}\n"
                f"Teacher: {student['Teacher_name']}"
            )

            self.status.setText("STUDENT SCANNED – WAITING FOR FETCHER")

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

        # 🔑 SYNC teacher overrides → fetcher state
        self.sync_fetched_from_global()

        self.check_and_mark_fetcher_completed()

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


    def activate_teacher(self, teacher):
        # Override fetcher
        self.active_teacher = teacher
        self.active_fetcher = None

        self.fetcher_panel.title_label.setText("TEACHER")

        # Display teacher in FETCHER panel
        self.fetcher_panel.image.setPixmap(
            self.load_photo(teacher.get("photo_path"))
        )
        self.fetcher_panel.name.setText( f"TEACHER ({teacher['Teacher_name']})")
        self.fetcher_panel.info.setText(
            f"Name: {teacher['Teacher_name']}\n"
            f"Grade: {teacher['Teacher_grade']}"
        )

        self.status.setText("TEACHER MODE – WAITING FOR STUDENT")
        self.status.setStyleSheet(
            "background:#0f766e;color:white;padding:10px;"
        )

        # Teacher auto-exit after 15 seconds
        self.teacher_timer.start(10000)

        if self.pending_student:
            student = self.pending_student
            self.pending_student = None
            self.try_pair(student)


    def activate_fetcher_from_holding(self, fetcher_rfid, student):
        holding = self.holding[fetcher_rfid]

        self.active_fetcher = holding["fetcher"]

        # 🔄 ALWAYS REFRESH ACTIVE STUDENTS FROM DATABASE
        self.fetcher_students = self.get_students(fetcher_rfid)

        # Keep previously fetched ones
        self.fetched_students = holding["fetched"]

        # Remove fetched entries that no longer exist (inactive students)
        active_ids = {s["Student_id"] for s in self.fetcher_students}
        self.fetched_students = {
            sid for sid in self.fetched_students if sid in active_ids
        }

        self.sync_fetched_from_global()

        self.check_and_mark_fetcher_completed()

        # 🔥 Freeze pagination on this fetcher's page
        self.holding_pagination_timer.stop()

        # Find correct page of this fetcher
        cards = sorted(
            self.holding.items(),
            key=lambda x: x[1]["expires"]
        )

        for index, (rfid, data) in enumerate(cards):
            if rfid == fetcher_rfid:
                self.holding_page_index = index // self.holding_cards_per_page
                break

        self.apply_holding_page()

        holding["widget"].hide()

        self.fetcher_panel.image.setPixmap(
            self.load_photo(self.active_fetcher.get("photo_path"))
        )
        self.fetcher_panel.name.setText(self.active_fetcher["Fetcher_name"])
        self.update_fetcher_student_list()

        self.try_pair(student)

        self.fetcher_timer.start(10000)

        
    def try_pair(self, student):
        mess = ""
        # ---------- TEACHER OVERRIDE ----------
        if self.active_teacher:

            # Student already fetched → same behavior
            if student["Student_id"] in self.fetched_students:

                # ✅ SHOW STUDENT INFO AGAIN (SAME AS FETCHER FLOW)
                self.student_panel.image.setPixmap(
                    self.load_photo(student.get("photo_path"))
                )
                self.student_panel.name.setText(student["Student_name"])
                self.student_panel.info.setText(
                    f"ID: {student['Student_id']}\n"
                    f"Grade: {student['grade_lvl']}\n"
                    f"Teacher: {student['Teacher_name']}"
                )

                self.status.setText("STUDENT HAS ALREADY BEEN FETCHED")
                self.status.setStyleSheet(
                    "background:#f59e0b;color:black;padding:10px;"
                )
                return

            # ✅ AUTHORIZATION RULE
            # Student.Teacher_name MUST match Teacher.Teacher_name
            if student["Teacher_name"] == self.active_teacher["Teacher_name"]:
                authorized = True
                status = "AUTHORIZED (TEACHER OVERRIDE)"
                mess ="AUTHORIZED"
            else:
                authorized = False
                status = "DENIED"
                mess = "DENIED"

            # Send result to Arduino
            self.serial.write(mess)

            # Sound + record
            if authorized:
                self.sound_authorized.play()
                self.fetched_students.add(student["Student_id"])
                self.globally_fetched_students.add(student["Student_rfid"])

                self.save_history(
                    f"TEACHER ({self.active_teacher['Teacher_name']})",
                    student["Student_name"],
                    status
                )

                self.save_to_history_log(
                    f"(OVERRIDE)Teacher: {self.active_teacher['Teacher_name']}",
                    student
                )

                self.student_fetched_by[student["Student_id"]] = (
                    "TEACHER",
                    self.active_teacher
                )

                for rfid, h in self.holding.items():
                    if student["Student_id"] in h["student_ids"]:

                        h["fetched"].add(student["Student_id"])

                        # 🔄 Refresh student list from DB
                        fresh_students = self.get_students(rfid)
                        active_ids = {s["Student_id"] for s in fresh_students}

                        h["students"] = fresh_students
                        h["student_ids"] = active_ids

                        # Clean fetched list
                        h["fetched"] = {
                            sid for sid in h["fetched"] if sid in active_ids
                        }

                        self.update_holding_display(rfid)

                        # ✅ FINAL COMPLETION CHECK WHILE IN HOLDING
                        if len(h["students"]) > 0 and \
                        len(h["fetched"]) == len(h["students"]):

                            self.completed_fetchers.add(rfid)
                            self.remove_from_holding(rfid)

                        break

                self.last_paired_type = "TEACHER"
                self.last_paired_data = self.active_teacher

                self.show_paired_by("TEACHER", self.active_teacher)
                QTimer.singleShot(8000, self.reset_student_after_pair)
                QTimer.singleShot(8000, self.reset_fetcher_panel_idle)
            else:
                self.sound_denied.play()
                
                self.save_history(
                f"TEACHER ({self.active_teacher['Teacher_name']})",
                student["Student_name"],
                status
            )


            # Status UI
            self.status.setText(status)
            self.status.setStyleSheet(
                f"background:{'#16a34a' if authorized else '#dc2626'};color:white;padding:10px;"
            )

            return  # 🚨 VERY IMPORTANT: STOP HERE

        # ==================================================
        # NORMAL FETCHER FLOW (UNCHANGED)
        # ==================================================

        if self.active_fetcher is None:
            return

        if student["Student_id"] in self.fetched_students:
            self.student_panel.image.setPixmap(
                self.load_photo(student.get("photo_path"))
            )
            self.student_panel.name.setText(student["Student_name"])
            self.student_panel.info.setText(
                f"ID: {student['Student_id']}\n"
                f"Grade: {student['grade_lvl']}\n"
                f"Teacher: {student['Teacher_name']}"
            )

            self.status.setText("STUDENT HAS ALREADY BEEN FETCHED")
            self.status.setStyleSheet(
                "background:#f59e0b;color:black;padding:10px;"
            )

            QTimer.singleShot(3000, self.reset_status_waiting_student)
            QTimer.singleShot(3000, self.safe_move_fetcher_to_holding)
            return

        self.cursor.execute("""
            SELECT * FROM registrations
            WHERE rfid=%s AND student_rfid=%s
        """, (
            self.active_fetcher["rfid"],
            student["Student_rfid"]   # ✅ use RFID, not student_id
        ))

        authorized = self.cursor.fetchone() is not None
        status = "AUTHORIZED" if authorized else "DENIED"
        self.serial.write(status)

        if authorized:
            self.sound_authorized.play()
        else:
            self.sound_denied.play()

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
            self.save_to_history_log(
                self.active_fetcher["Fetcher_name"],
                student
            )

        if authorized:
            self.fetched_students.add(student["Student_id"])
            self.globally_fetched_students.add(student["Student_rfid"])
            self.student_fetched_by[student["Student_id"]] = (
                "FETCHER",
                self.active_fetcher
            )

            # 🔥 FORCE SYNC TO HOLDING IMMEDIATELY
            rfid = self.active_fetcher["rfid"]
            if rfid in self.holding:
                self.holding[rfid]["fetched"].add(student["Student_id"])

            self.show_paired_by("FETCHER", self.active_fetcher)
            QTimer.singleShot(4000, self.reset_student_after_pair)
            QTimer.singleShot(4000, self.safe_move_fetcher_to_holding)
            self.update_fetcher_student_list()
            self.update_holding_display(self.active_fetcher["rfid"])

            # 🔄 Refresh active students before completion check
            self.fetcher_students = self.get_students(self.active_fetcher["rfid"])

            active_ids = {s["Student_id"] for s in self.fetcher_students}
            self.fetched_students = {
                sid for sid in self.fetched_students if sid in active_ids
            }

            if len(self.fetcher_students) > 0 and \
            len(self.fetched_students) == len(self.fetcher_students):

                self.completed_fetchers.add(self.active_fetcher["rfid"])
                self.remove_from_holding(self.active_fetcher["rfid"])
                QTimer.singleShot(3000, self.reset_all)
                return

            

        self.student_display_timer.start(3000)



    # ---------------- HOLDING ----------------
    def move_fetcher_to_holding(self):

        if self.active_teacher:
            self.reset_teacher_mode()
            return
        
        if not self.active_fetcher:
            return

        rfid = self.active_fetcher["rfid"]

        # 🔄 Always refresh before creating holding card
        self.fetcher_students = self.get_students(rfid)

        active_ids = {s["Student_id"] for s in self.fetcher_students}

        self.fetched_students = {
            sid for sid in self.fetched_students if sid in active_ids
        }

        self.sync_fetched_from_global()

        # ✅ Final completion check
        if len(self.fetcher_students) > 0 and \
        len(self.fetched_students) == len(self.fetcher_students):

            self.completed_fetchers.add(rfid)
            self.remove_from_holding(rfid)
            self.reset_all()
            return

        if rfid in self.holding and self.active_fetcher is None:
            return

        if rfid in self.holding:
            self.return_fetcher_to_holding(rfid)

            # 🔥 RESTART SCROLLING AFTER FETCHER RETURNS
            if not self.holding_pagination_timer.isActive():
                self.holding_pagination_timer.start(4000)

            self.reset_all()
            return

        # OUTER CARD
        box = QFrame()
        box.setStyleSheet(
            "background:#e5e7eb;border-radius:10px;padding:2px;"
        )

        # 🔁 HORIZONTAL LAYOUT
        h = QHBoxLayout(box)
        h.setSpacing(10)

        # LEFT: FETCHER PHOTO
        img = QLabel(alignment=Qt.AlignCenter)
        img.setPixmap(self.load_photo(self.active_fetcher.get("photo_path")))
        img.setFixedSize(100, 100)
        img.setScaledContents(True)
        h.addWidget(img)

        # RIGHT: NAME + STUDENT LIST (VERTICAL)
        v = QVBoxLayout()
        v.setSpacing(3)

        # FETCHER NAME
        name = QLabel(self.active_fetcher["Fetcher_name"])
        name.setFont(QFont("Segoe UI", 12, QFont.Bold))
        v.addWidget(name)

        # STUDENT LIST
        student_labels = []
        for s in self.fetcher_students:
            lbl = QLabel("• " + s["Student_name"])
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet(
                "color:green;" if s["Student_id"] in self.fetched_students else "color:gray;"
            )
            v.addWidget(lbl)
            student_labels.append(lbl)

        h.addLayout(v)
        

        # SAVE TO HOLDING QUEUE (LOGIC UNCHANGED)
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
        self.holding_page_index = 0
        self.update_holding_pagination()

    def cleanup_holding(self):
        now = datetime.now()
        for rfid in list(self.holding.keys()):
            if self.holding[rfid]["expires"] < now:
                self.remove_from_holding(rfid)

                

    def remove_from_holding(self, fetcher_rfid):
        if fetcher_rfid in self.holding:
            self.holding[fetcher_rfid]["widget"].deleteLater()
            del self.holding[fetcher_rfid]
            self.holding_page_index = 0
            self.update_holding_pagination()

            # 🔥 Ensure scrolling continues after removal
            if not self.holding_pagination_timer.isActive():
                self.holding_pagination_timer.start(4000)

    # ---------------- HELPERS ----------------
    def get_students(self, rfid):
        self.cursor.execute("""
            SELECT student_id AS Student_id,
                student_rfid AS Student_rfid,
                student_name AS Student_name
            FROM registrations
            WHERE rfid=%s
            AND status='Active'
        """, (rfid,))
        return self.cursor.fetchall()

    def update_fetcher_student_list(self):
        html = "<b>Students to fetch:</b><br>"
        for s in self.fetcher_students:
            color = "green" if s["Student_id"] in self.fetched_students else "gray"
            html += f"<span style='color:{color}; font-weight:bold'>• {s['Student_name']}</span><br>"
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

        if self.replay_mode:
            return

        self.fetcher_panel.title_label.setText("FETCHER")
        self.fetcher_panel.name.setText("WAITING...")
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
    
    def save_to_history_log(self, fetcher_name, student):
        try:
            self.cursor.execute("""
                INSERT INTO history_log
                (fetcher_name, student_name, student_id, grade, teacher, location, time_out)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (
                fetcher_name,
                student["Student_name"],
                student["Student_id"],
                student["grade_lvl"],
                student["Teacher_name"],
                "Main Gate"
            ))

            self.db.commit()

        except Exception as e:
            print("History log DB error:", e)

    def update_clock(self):
        now = datetime.now()
        self.date_label.setText(now.strftime("%A, %B %d, %Y"))
        self.time_label.setText(now.strftime("%I:%M:%S %p"))

    def show_temp_status(self, text, bg="#f59e0b", fg="black", delay=3000):
        self.status.setText(text)
        self.status.setStyleSheet(
            f"background:{bg};color:{fg};padding:10px;"
        )
        QTimer.singleShot(delay, self.reset_status_waiting_rfid)

    def reset_status_waiting_rfid(self):
        self.status.setText("WAITING FOR RFID...")
        self.status.setStyleSheet(
            "background:#6b7280;color:white;padding:10px;"
        )
    def return_fetcher_to_holding(self, rfid):
        if rfid in self.holding:
            widget = self.holding[rfid].get("widget")
            if widget:
                widget.show()

    def closeEvent(self, event):
        if self.serial:
            self.serial.stop()
            self.serial.wait()
        event.accept()
    
    def safe_move_fetcher_to_holding(self):
        if not self.active_fetcher:
            return

        rfid = self.active_fetcher["rfid"]

        # 🔄 Always refresh active students from DB
        self.fetcher_students = self.get_students(rfid)

        active_ids = {s["Student_id"] for s in self.fetcher_students}

        # 🔄 Clean fetched list
        self.fetched_students = {
            sid for sid in self.fetched_students if sid in active_ids
        }

        # 🔄 Sync global fetched
        self.sync_fetched_from_global()

        # ✅ FINAL COMPLETION CHECK BEFORE HOLDING
        if len(self.fetcher_students) > 0 and \
        len(self.fetched_students) == len(self.fetcher_students):

            self.completed_fetchers.add(rfid)
            self.remove_from_holding(rfid)
            self.reset_all()
            return

        # 🔄 Update holding dictionary BEFORE move
        if rfid in self.holding:
            self.holding[rfid]["students"] = self.fetcher_students
            self.holding[rfid]["fetched"] = self.fetched_students
            self.holding[rfid]["student_ids"] = active_ids

        self.move_fetcher_to_holding()
    
    def update_holding_display(self, fetcher_rfid):
        if fetcher_rfid not in self.holding:
            return

        holding = self.holding[fetcher_rfid]

        # 🔄 Always re-sync from DB before coloring
        fresh_students = self.get_students(fetcher_rfid)
        active_ids = {s["Student_id"] for s in fresh_students}

        holding["students"] = fresh_students
        holding["student_ids"] = active_ids

        holding["fetched"] = {
            sid for sid in holding["fetched"] if sid in active_ids
        }

        for lbl, s in zip(holding["labels"], holding["students"]):
            lbl.setStyleSheet(
                "color:green;" if s["Student_id"] in holding["fetched"] else "color:gray;"
            )

    def reset_teacher_mode(self):
        self.active_teacher = None
        self.teacher_timer.stop()
        self.fetcher_panel.title_label.setText("FETCHER")
        self.reset_all()

    def show_paired_by(self, person_type, data):
        """
        person_type: 'FETCHER' or 'TEACHER'
        data: fetcher or teacher row
        """

        if person_type == "TEACHER":
            self.fetcher_panel.title_label.setText("TEACHER")
            self.fetcher_panel.name.setText(f"TEACHER ({data['Teacher_name']})")
            self.fetcher_panel.info.setText(
                f"Name: {data['Teacher_name']}\n"
                f"Grade: {data['Teacher_grade']}"
            )
            self.fetcher_panel.image.setPixmap(
                self.load_photo(data.get("photo_path"))
            )

        else:  # FETCHER
            self.fetcher_panel.title_label.setText("FETCHER")
            self.fetcher_panel.name.setText(data["Fetcher_name"])
            self.fetcher_panel.info.setText(
                f"Students fetched: {len(self.fetched_students)}"
            )
            self.fetcher_panel.image.setPixmap(
                self.load_photo(data.get("photo_path"))
            )
    
    def reset_student_after_pair(self):
        self.student_panel.image.setPixmap(self.load_photo(None))
        self.student_panel.name.setText("WAITING...")
        self.student_panel.info.setText("")

        self.status.setText("WAITING FOR RFID...")
        self.status.setStyleSheet(
        "background:#6b7280;color:white;padding:10px;"
        )

    def reset_fetcher_panel_idle(self):
        self.fetcher_panel.title_label.setText("FETCHER")
        self.fetcher_panel.image.setPixmap(self.load_photo(None))
        self.fetcher_panel.name.setText("WAITING...")
        self.fetcher_panel.info.setText("")

    def return_fetcher_to_holding_and_idle(self):
        # Return fetcher visually back to holding (NO recreation)
        self.return_existing_fetcher_to_holding()

        # Reset fetcher panel UI only
        self.reset_fetcher_panel_idle()

        # Final idle status
        self.status.setText("WAITING FOR RFID...")
        self.status.setStyleSheet(
            "background:#6b7280;color:white;padding:10px;"
        )

    def show_fetcher_from_holding_temporarily(self, student_id):
        """
        Find the fetcher in holding who already fetched this student,
        show them in ACTIVE for a few seconds, then return to holding.
        """
        for rfid, h in self.holding.items():
            if student_id in h["fetched"]:
                fetcher = h["fetcher"]

                # 🔹 Temporarily restore active fetcher
                self.active_fetcher = fetcher
                self.fetcher_students = h["students"]
                self.fetched_students = h["fetched"]

                # 🔑 IMPORTANT: sync paired state
                self.last_paired_type = "FETCHER"
                self.last_paired_data = fetcher

                # 🔹 Show fetcher in ACTIVE panel
                self.show_paired_by("FETCHER", fetcher)
                self.fetcher_panel.title_label.setText("FETCHER")
                self.update_fetcher_student_list()

                # Hide holding card while active
                h["widget"].hide()

                # 🔒 Lock UI for 4 seconds before returning
                QTimer.singleShot(4000, self.return_fetcher_to_holding_and_idle)

                return
        
    def return_existing_fetcher_to_holding(self):
        if not self.active_fetcher:
            return

        target_rfid = self.active_fetcher["rfid"]

        # 🔥 STOP auto rotation temporarily
        self.holding_pagination_timer.stop()

        # Same sorting used in pagination
        cards = sorted(
            self.holding.items(),
            key=lambda x: x[1]["expires"]
        )

        # Find index of this fetcher
        for index, (rfid, data) in enumerate(cards):

            if rfid == target_rfid:

                target_page = index // self.holding_cards_per_page
                self.holding_page_index = target_page
                break

        # Reset active state
        self.active_fetcher = None
        self.fetcher_students = []
        self.fetched_students = set()

        # Force redraw
        self.apply_holding_page()

        def restart_timer():
            if not self.holding_pagination_timer.isActive():
                self.holding_pagination_timer.start(4000)

        QTimer.singleShot(500, restart_timer)

    def end_replay_mode(self):
         # 🔓 unlock first
        self.replay_mode = False

        # Clear student panel
        self.student_panel.image.setPixmap(self.load_photo(None))
        self.student_panel.name.setText("WAITING...")
        self.student_panel.info.setText("")

        # Return fetcher to holding
        self.return_existing_fetcher_to_holding()

        # Reset fetcher UI
        self.reset_fetcher_panel_idle()

        # Final idle status
        self.status.setText("WAITING FOR RFID...")
        self.status.setStyleSheet(
            "background:#6b7280;color:white;padding:10px;"
        )

    def sync_fetched_from_global(self):
        """
        Ensure fetched_students reflects global fetched state
        (used when fetcher becomes active AFTER teacher override)
        """
        if not self.active_fetcher:
            return

        for s in self.fetcher_students:
            if s["Student_rfid"] in self.globally_fetched_students:
                self.fetched_students.add(s["Student_id"])
    
    def check_and_mark_fetcher_completed(self):
        """
        If all students of the active fetcher are fetched,
        mark the fetcher as completed and block future taps.
        """
        if not self.active_fetcher:
            return

        if len(self.fetcher_students) == 0:
            return

        if len(self.fetched_students) == len(self.fetcher_students):
            self.completed_fetchers.add(self.active_fetcher["rfid"])

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_holding_pagination()

    def update_holding_pagination(self):
        if not self.holding:
            return

        # Approximate height of one holding card
        card_height = 140  # adjust if needed

        available_height = self.height() - 300

        per_page = max(1, available_height // card_height)

        if per_page != self.holding_cards_per_page:
            self.holding_cards_per_page = per_page
            self.holding_page_index = 0

        self.apply_holding_page()

    def apply_holding_page(self):
        # 🔒 Just remove from layout — DO NOT remove parent
        while self.holding_layout.count():
            item = self.holding_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()

        # Always keep consistent order
        cards = sorted(
            self.holding.values(),
            key=lambda x: x["expires"]
        )

        total = len(cards)
        if total == 0:
            return

        total_pages = (total - 1) // self.holding_cards_per_page + 1

        if self.holding_page_index >= total_pages:
            self.holding_page_index = 0

        start = self.holding_page_index * self.holding_cards_per_page
        end = start + self.holding_cards_per_page

        # 🔥 Show only widgets in this page
        for i in range(start, min(end, total)):
            widget = cards[i]["widget"]
            self.holding_layout.addWidget(widget)
            widget.show()
    
    def rotate_holding_page(self):

        total_cards = len(self.holding)

        if total_cards == 0:
            return

        total_pages = (total_cards - 1) // self.holding_cards_per_page + 1

        if total_pages <= 1:
            self.holding_page_index = 0
            self.apply_holding_page()
            return

        self.holding_page_index += 1

        if self.holding_page_index >= total_pages:
            self.holding_page_index = 0

        self.apply_holding_page()


# ---------------- RUN ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RFIDTapping()
    window.show()
    sys.exit(app.exec_())
