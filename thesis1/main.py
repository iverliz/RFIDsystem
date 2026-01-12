import tkinter as tk
import os

from frames.login import LoginFrame, SignUpFrame
from frames.main_dashboard import MainDashboard
from frames.student_record import StudentRecord
from frames.teacher_record import TeacherRecord
from frames.fetcher_record import FetcherRecord
from frames.rfid_registration import RfidRegistration
from frames.history_log import RFIDHistory
from frames.report import Report
from frames.account import Account
from frames.enrollthisyear import EnrollThisYear


SESSION_FILE = "session.txt"


class Rfid(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("RFID MANAGEMENT SYSTEM - Cainta Catholic College ")
        self.geometry("1350x700+0+0")

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}

        for FrameClass in (
            LoginFrame,
            SignUpFrame,
            MainDashboard,
            StudentRecord,
            TeacherRecord,
            FetcherRecord,
            RfidRegistration,
            RFIDHistory,
            Report,
            Account,
            EnrollThisYear
        ):
            frame = FrameClass(container, self)
            self.frames[FrameClass.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        # Initial screen
        if os.path.exists(SESSION_FILE):
            self.show_frame("MainDashboard")
        else:
            self.show_frame("LoginFrame")

    def show_frame(self, name):
        # Allow Login & SignUp without session
        if name not in ("LoginFrame", "SignUpFrame") and not os.path.exists(SESSION_FILE):
            name = "LoginFrame"

        if name == "LoginFrame":
            frame = self.frames["LoginFrame"]
            if hasattr(frame, "username"):
                frame.username.delete(0, tk.END)
            if hasattr(frame, "password"):
                frame.password.delete(0, tk.END)

        self.frames[name].tkraise()


if __name__ == "__main__":
    Rfid().mainloop()
