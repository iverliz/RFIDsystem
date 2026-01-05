import tkinter as tk
import os

from frames.login import App
from frames.main_dashboard import MainDashboard
from frames.student_record import StudentRecord
from frames.teacher_record import TeacherRecord
from frames.fetcher_record import FetcherRecord
from re
from frames.history_log import RFIDHistory
from frames.report import Report
from frames.account import Account

SESSION_FILE = "session.txt"


class Rfid(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("RFID MANAGEMENT SYSTEM")
        self.geometry("1350x700+0+0")

        self.frames = {}

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        # REGISTER ALL FRAMES HERE
        for FrameClass in (
            MainDashboard,
            StudentRecord,
            TeacherRecord,
            FetcherRecord,
            RFIDHistory,
            Report,
            Account
        ):
            frame = FrameClass(container, self)
            self.frames[FrameClass.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("MainDashboard")

    def show_frame(self, name):
        self.frames[name].tkraise()

    def logout(self):
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        self.destroy()
        App().mainloop()


def start_app():
    if os.path.exists(SESSION_FILE):
        Rfid().mainloop()
    else:
        App().mainloop()


if __name__ == "__main__":
    start_app()
