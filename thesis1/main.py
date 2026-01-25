import tkinter as tk
import os

from frames.login import LoginFrame, SignUpFrame, ForgotPasswordFrame
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

        self.title("RFID MANAGEMENT SYSTEM - Cainta Catholic College ")
        self.geometry("1350x700+0+0")

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}

        for FrameClass in (
            LoginFrame,
            SignUpFrame,
            ForgotPasswordFrame,
            MainDashboard,
            StudentRecord,
            TeacherRecord,
            FetcherRecord,
            RfidRegistration,
            RFIDHistory,
            Report,
            Account
        ):
            frame = FrameClass(container, self)
            self.frames[FrameClass.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        
        if os.path.exists(SESSION_FILE):
            self.show_frame("MainDashboard")
        else:
            self.show_frame("LoginFrame")

    def show_frame(self, name):
        # 1. First, tell the RFID page to STOP if we are leaving it
        if "RfidRegistration" in self.frames:
            self.frames["RfidRegistration"].stop_listening()

        if name not in ("LoginFrame", "SignUpFrame", "ForgotPasswordFrame") and not os.path.exists(SESSION_FILE):
            name = "LoginFrame"
  
        # 2. Existing Login cleanup logic...
        if name == "LoginFrame":
            frame = self.frames["LoginFrame"]
            if hasattr(frame, "username"): frame.username.delete(0, tk.END)
            if hasattr(frame, "password"): frame.password.delete(0, tk.END)

        # 3. If we are entering the Registration page, START the serial connection
        if name == "RfidRegistration":
            self.frames[name].start_listening()

        self.frames[name].tkraise()


if __name__ == "__main__":
    Rfid().mainloop()
