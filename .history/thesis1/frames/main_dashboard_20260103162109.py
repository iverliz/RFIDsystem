import tkinter as tk
import os

from frames.login import App
from frames.main_dashboard import MainDashboard
from frames.student_record import StudentRecord
from frames.teacher_record import TeacherRecord
from frames.fetcher_record import FetcherRecord
from frames.history_log import RFIDHistory
from frames.account import Account
from frames.report import Report

SESSION_FILE = "session.txt"


class Rfid(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("RFID MANAGEMENT SYSTEM")
        self.geometry("1350x700+0+0")

        # 🔹 Main container
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}

        # 🔹 Register ALL frames with controller
        for FrameClass in (
            MainDashboard,
            StudentRecord,
            TeacherRecord,
            FetcherRecord,
            RFIDHistory,
            Account,
            Report
        ):
            frame = FrameClass(container, self)  # ✅ PASS CONTROLLER
            self.frames[FrameClass.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("MainDashboard")

    def show_frame(self, name):
        if name in self.frames:
            self.frames[name].tkraise()
        else:
            print(f"[ERROR] Frame not found: {name}")

    def logout(self):
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        self.destroy()
        App().mainloop()


def start_app():
    if os.path.exists(SESSION_FILE):
        app = Rfid()
        app.mainloop()
    else:
        App().mainloop()


if __name__ == "__main__":
    start_app()
