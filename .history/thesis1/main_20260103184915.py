import tkinter as tk
import os

from frames.login import LoginFrame, SignUpFrame
from frames.main_dashboard import MainDashboard
from frames.main_dashboard import MainDashboard
from frames.student_record import StudentRecord
from frames.teacher_record import TeacherRecord
from frames.fetcher_record import FetcherRecord
from frames.rfid_registration import RfidRegistration
from frames.history_log import RFIDHistory
from frames.report import Report
from frames.account import Account

SESSION_FILE = "session.txt"


class Rfid(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("RFID MANAGEMENT SYSTEM")
        self.geometry("1350x700+0+0")

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}

        for FrameClass in (
            App,
            MainDashboard,
            StudentRecord,
            RfidRegistration,
            TeacherRecord,
            FetcherRecord,
            RFIDHistory,
            Report,
            Account
        ):
            frame = FrameClass(container, self)
            self.frames[FrameClass.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        # show correct first screen
        if os.path.exists(SESSION_FILE):
            self.show_frame("MainDashboard")
        else:
            self.show_frame("App")

    def show_frame(self, name):
        self.frames[name].tkraise()


if __name__ == "__main__":
    Rfid().mainloop()
