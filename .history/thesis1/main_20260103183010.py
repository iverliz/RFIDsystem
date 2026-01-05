import tkinter as tk
import os

from frames.login import App
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

        self.frames = {}

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        # Initialize frames
        for FrameClass in (
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

        # Default show MainDashboard frame after app starts
        self.show_frame("MainDashboard")

    def show_frame(self, name):
        print(f"Switching to {name} frame.")  # Debugging line
        frame = self.frames.get(name)
        if frame:
            frame.tkraise()
        else:
            print(f"Error: Frame {name} not found!")

    def logout(self):
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        self.destroy()
        App().mainloop()


def start_app():
    if os.path.exists(SESSION_FILE):
        print("Session found, starting RFID app...")
        app = Rfid()
        app.mainloop()
    else:
        print("No session found, starting login...")
        App().mainloop()


if __name__ == "__main__":
    start_app()
