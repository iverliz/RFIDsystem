import sys
import time
import serial
from datetime import datetime
import mysql.connector


from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QFrame
)

# ---------------- RFID DATA ----------------
rfid_names = {
    "46E24C05": "Lozano, John Kent",
    "B9CF6E11": "Llorera, Mark",
    "660CE9B8": "Burgos, John Iverson",
    "4F7F4FDE": "Balderama, John Carlo"
}

student_info = {
    "B9CF6E11": {"grade": "Grade 6", "section": "A", "teacher": "Mrs. Ahveline"},
    "4F7F4FDE": {"grade": "Grade 5", "section": "B", "teacher": "Mr. Ahveline"}
}

valid_pairs = {
    ("46E24C05", "B9CF6E11"),
    ("B9CF6E11", "46E24C05"),
    ("660CE9B8", "4F7F4FDE"),
    ("4F7F4FDE", "660CE9B8")
}

rfid_images = {
    "46E24C05": "images/kent.jpg",
    "B9CF6E11": "images/mark.jpg",
    "660CE9B8": "images/iverson.jpg",
    "4F7F4FDE": "images/baldy.jpg"
}

# ---------------- SERIAL THREAD ----------------
class SerialThread(QThread):
    uid_scanned = pyqtSignal(str)

    def __init__(self, port="COM3", baud=9600):
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
                    uid = uid.split(":")[-1].strip().upper()
                    self.uid_scanned.emit(uid)
        except Exception as e:
            print("Serial error:", e)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


# ---------------- MAIN WINDOW ----------------
class RFIDTapping(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RFID Tapping System")
        self.setGeometry(100, 100, 1100, 750)

        self.stage = "first"
        self.first_uid = None
        self.second_uid = None

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # ---------------- LEFT SIDE (Fetcher + Student) ----------------
        left_layout = QHBoxLayout()

        self.fetcher_panel = self.create_person_panel("Fetcher", "#1e3a8a")
        self.student_panel = self.create_person_panel("Student", "#047857")

        left_layout.addWidget(self.fetcher_panel)
        left_layout.addWidget(self.student_panel)

        # ---------------- RIGHT SIDE (History Only) ----------------
        right_layout = QVBoxLayout()

        # 🔹🔹🔹 ADDED MAIN TITLE 🔹🔹🔹
        system_title = QLabel("RFID Fetcher - Student System")
        system_title.setAlignment(Qt.AlignCenter)
        system_title.setStyleSheet(
            "background:#047857; color:white; padding:12px;"
        )
        system_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        right_layout.addWidget(system_title)
        # 🔹🔹🔹 END OF ADDED CODE 🔹🔹🔹

        history_title = QLabel("HISTORY LOG")
        history_title.setAlignment(Qt.AlignCenter)
        history_title.setStyleSheet("background:#1e3a8a;color:white;padding:10px;")
        history_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        right_layout.addWidget(history_title)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Fetcher", "Student", "Time"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_layout.addWidget(self.table)

        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 1)

        # ---------------- SERIAL ----------------
        try:
            self.serial_thread = SerialThread("COM3")
            self.serial_thread.uid_scanned.connect(self.process_rfid)
            self.serial_thread.start()
        except Exception as e:
            QMessageBox.warning(self, "Warning", str(e))

    # ---------------- PERSON PANEL ----------------
    def create_person_panel(self, title, color):
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)

        layout = QVBoxLayout(frame)

        lbl = QLabel(title.upper())
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(f"background:{color};color:white;padding:5px;")
        lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(lbl)

        img = QLabel()
        img.setAlignment(Qt.AlignCenter)
        pix = QPixmap(150, 150)
        pix.fill(Qt.lightGray)
        img.setPixmap(pix)
        layout.addWidget(img)

        name = QLabel("[No Data]")
        name.setAlignment(Qt.AlignCenter)
        name.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(name)

        info = QLabel("")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

        time_lbl = QLabel("")
        time_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(time_lbl)

        frame.image = img
        frame.name = name
        frame.info = info
        frame.time = time_lbl
        return frame

    # ---------------- RFID LOGIC ----------------
    def process_rfid(self, uid):
        name = rfid_names.get(uid, "Unknown")

        if self.stage == "first":
            self.first_uid = uid
            self.update_panel(self.fetcher_panel, uid, name)
            self.stage = "second"

        else:
            self.second_uid = uid
            self.update_panel(self.student_panel, uid, name, True)
            self.stage = "first"
            self.check_pair()

    def check_pair(self):
        pair = (self.first_uid, self.second_uid)
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if pair in valid_pairs:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(rfid_names[self.first_uid]))
            self.table.setItem(row, 1, QTableWidgetItem(rfid_names[self.second_uid]))
            self.table.setItem(row, 2, QTableWidgetItem(time_now))

        QThread.msleep(1500)
        self.clear_panels()

    # ---------------- UI HELPERS ----------------
    def update_panel(self, panel, uid, name, student=False):
        pix = QPixmap(rfid_images.get(uid, ""))
        if pix.isNull():
            pix = QPixmap(150, 150)
            pix.fill(Qt.gray)

        panel.image.setPixmap(pix.scaled(150, 150, Qt.KeepAspectRatio))
        panel.name.setText(name)
        panel.time.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        if student:
            info = student_info.get(uid, {})
            panel.info.setText(
                f"{info.get('grade','')} | {info.get('section','')}\nTeacher: {info.get('teacher','')}"
            )

    def clear_panels(self):
        for panel in (self.fetcher_panel, self.student_panel):
            pix = QPixmap(150, 150)
            pix.fill(Qt.lightGray)
            panel.image.setPixmap(pix)
            panel.name.setText("[No Data]")
            panel.info.setText("")
            panel.time.setText("")


# ---------------- RUN ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RFIDTapping()
    window.show()
    sys.exit(app.exec_())
