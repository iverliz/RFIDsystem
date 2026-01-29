import tkinter as tk
from frames.login import LoginFrame, SignUpFrame, ForgotPasswordFrame
from frames.main_dashboard import MainDashboard
from frames.student_record import StudentRecord
from frames.teacher_record import TeacherRecord
from frames.fetcher_record import FetcherRecord
from frames.rfid_registration import RfidRegistration
from frames.history_log import RFIDHistory
from frames.report import Report
from frames.account import Account

class Rfid(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("RFID MANAGEMENT SYSTEM - Cainta Catholic College")
        self.geometry("1350x700+0+0")

        # This is your 'Memory Session'. If this has data, you are logged in.
        self.current_user = None 

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}

        for FrameClass in (
            LoginFrame, SignUpFrame, ForgotPasswordFrame,
            MainDashboard, StudentRecord, TeacherRecord,
            FetcherRecord, RfidRegistration, RFIDHistory,
            Report, Account
        ):
            frame = FrameClass(container, self)
            self.frames[FrameClass.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("LoginFrame")

    def show_frame(self, name):
        
        restricted_pages = ["MainDashboard", "StudentRecord", "TeacherRecord", 
                            "FetcherRecord", "RfidRegistration", "RFIDHistory", 
                            "Report", "Account"]
        
        # If not logged in and trying to access a restricted page
        if name in restricted_pages and self.current_user is None:
            # ONLY redirect to login if we aren't already there
            if name != "LoginFrame":
                self.frames["LoginFrame"].tkraise()
                return

        if name == "LoginFrame":
            frame = self.frames["LoginFrame"]
            if hasattr(frame, "username"): frame.username.delete(0, tk.END)
            if hasattr(frame, "employee_id"): frame.employee_id.delete(0, tk.END)
            if hasattr(frame, "password"): frame.password.delete(0, tk.END)

        # 3. Handle RFID logic
        if name == "RfidRegistration":
            self.frames[name].start_listening()
        else:
            if "RfidRegistration" in self.frames:
                self.frames["RfidRegistration"].stop_listening()

        self.frames[name].tkraise()
    def login_success(self, user_data):
        """Called by LoginFrame when DB check passes"""
        self.current_user = user_data  # Session starts in RAM here
        self.show_frame("MainDashboard")

    def logout(self):
        """Called by Logout Button in Dashboard"""
        self.current_user = None       
        self.show_frame("LoginFrame")

if __name__ == "__main__":
    app = Rfid()
    app.mainloop()