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

        # Initial show MainDashboard after login
        print("App initialized. Now showing MainDashboard.")
        self.show_frame("MainDashboard")

    def show_frame(self, name):
        print(f"Attempting to switch to {name} frame.")  # Debugging line
        frame = self.frames.get(name)
        if frame:
            frame.tkraise()
            print(f"Successfully switched to {name} frame.")  # Debugging line
        else:
            print(f"Error: Frame {name} not found!")

    def logout(self):
        print("Logging out...")  # Debugging line
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
            print(f"Session file {SESSION_FILE} deleted.")  # Debugging line
        self.destroy()
        App().mainloop()  # Going back to the login screen


def start_app():
    print("Starting app...")  # Debugging line
    if os.path.exists(SESSION_FILE):
        print("Session found. Starting RFID application.")  # Debugging line
        app = Rfid()
        app.mainloop()
    else:
        print("No session file found. Starting login screen.")  # Debugging line
        App().mainloop()


if __name__ == "__main__":
    start_app()
