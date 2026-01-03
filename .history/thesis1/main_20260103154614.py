import tkinter as tk
from frames.login import App
from frames.main_dashboard import MainDashboard
from frames.history_log import RFIDHistory
from frames.report import Report
from frames.account import Account
from frames.teacher_record import TeacherRecord
from frames.student_record import StudentRecord
from frames.fetcher_record import FetcherRecord
import os


SESSION_FILE = "session.txt"


class Rfid(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("RFID MANAGEMENT SYSTEM")
        self.geometry("1350x700+0+0")

        self.frames = {}

        for F in (
            App,
            MainDashboard,
            RFIDHistory,
            Report,
            Account,
            TeacherRecord,
            StudentRecord,
            FetcherRecord,
        ):
            frame = F(self)
            self.frames[F.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        # Decide which screen to show first
        if self.is_logged_in():
            self.show_frame("MainDashboard")
        else:
            self.show_frame("App")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def is_logged_in(self):
        return os.path.exists(SESSION_FILE)

    def login_success(self):
        with open(SESSION_FILE, "w") as f:
            f.write("logged_in")
        self.show_frame("MainDashboard")

    def logout(self):
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        self.show_frame("App")


if __name__ == "__main__":
    app = Rfid()
    app.mainloop()
