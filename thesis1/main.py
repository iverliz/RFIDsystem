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
from frames.Classroom import ClassroomFrame

class Rfid(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("RFID MANAGEMENT SYSTEM - Cainta Catholic College")
        self.geometry("1350x700+0+0")

        # Session data: stores username, employee_id, and role
        self.current_user = None 

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}

        # Initial frames that don't require login data to exist
        for FrameClass in (LoginFrame, SignUpFrame, ForgotPasswordFrame):
            frame = FrameClass(self.container, self)
            self.frames[FrameClass.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("LoginFrame")

    def show_frame(self, name):
        restricted_pages = [
            "MainDashboard", "StudentRecord", "TeacherRecord","ClassroomFrame",
            "FetcherRecord", "RfidRegistration", "RFIDHistory", 
            "Report", "Account"
        ]
        
        # 1. Security Check: Redirect to login if trying to access restricted pages without a session
        if name in restricted_pages and self.current_user is None:
            self.show_frame("LoginFrame")
            return

        # 2. Admin vs Teacher Restriction: 
        # Teachers should not be able to access Teacher Records or RFID Registration
        if self.current_user and self.current_user.get("role") == "Teacher":
            admin_only = ["TeacherRecord", "RfidRegistration", " StudentRecord ", "FetcherRecord", "RFIDHistory", "Report", "Account"]
            if name in admin_only:
                tk.messagebox.showwarning("Access Denied", "Teachers do not have permission to access this module.")
                return

        # 3. Clean up Login fields if going back to Login
        if name == "LoginFrame":
            frame = self.frames.get("LoginFrame")
            if frame:
                if hasattr(frame, "username"): frame.username.delete(0, tk.END)
                if hasattr(frame, "employee_id"): frame.employee_id.delete(0, tk.END)
                if hasattr(frame, "password"): frame.password.delete(0, tk.END)

        # 4. Handle RFID logic for scanning
        if name == "RfidRegistration" and name in self.frames:
            self.frames[name].start_listening()
        else:
            if "RfidRegistration" in self.frames:
                self.frames["RfidRegistration"].stop_listening()

        self.frames[name].tkraise()

    def login_success(self, user_data):
        """Called by LoginFrame when DB check passes"""
        self.current_user = user_data  
        
        # Add ClassroomFrame to the loop
        for FrameClass in (
            MainDashboard, StudentRecord, TeacherRecord,
            FetcherRecord, RfidRegistration, RFIDHistory,
            Report, Account, ClassroomFrame  
        ):
            frame = FrameClass(self.container, self)
            self.frames[FrameClass.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("MainDashboard")

    def logout(self):
        """Called by Logout Button in Dashboard"""
        self.current_user = None 
        # Clear sensitive frames from memory on logout
        for name in list(self.frames.keys()):
            if name not in ["LoginFrame", "SignUpFrame", "ForgotPasswordFrame"]:
                self.frames[name].destroy()
                del self.frames[name]
                
        self.show_frame("LoginFrame")

if __name__ == "__main__":
    app = Rfid()
    app.mainloop()