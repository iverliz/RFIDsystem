import tkinter as tk
from tkinter import messagebox
import serial
import threading
import serial.tools.list_ports
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
from frames.overrride import OverrideFrame

class Rfid(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("RFID MANAGEMENT SYSTEM - Cainta Catholic College")
        self.geometry("1350x700+0+0")

        # --- SESSION & STATE ---
        self.current_user = None 
        self.current_frame_name = "LoginFrame"
        self.ser = None
        self.running = True 

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}

        # Load initial frames
        for FrameClass in (LoginFrame, SignUpFrame, ForgotPasswordFrame):
            frame = FrameClass(self.container, self)
            self.frames[FrameClass.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("LoginFrame")
        
        # Start the global Arduino listener
        self.start_serial_listener()

    def show_frame(self, name):
        restricted_pages = [
            "MainDashboard", "StudentRecord", "TeacherRecord","ClassroomFrame",
            "FetcherRecord", "RfidRegistration","OverrideFrame", "RFIDHistory", 
            "Report", "Account"
        ]
        
        # Security & Role Checks
        if name in restricted_pages and self.current_user is None:
            self.show_frame("LoginFrame")
            return

        if self.current_user and self.current_user.get("role") == "Teacher":
            admin_only = ["TeacherRecord", "RfidRegistration", "StudentRecord", "FetcherRecord", "RFIDHistory", "Report", "Account"]
            if name in admin_only:
                messagebox.showwarning("Access Denied", "Teachers do not have permission to access this module.")
                return

        # Navigation logic
        self.current_frame_name = name
        self.frames[name].tkraise()

    

    def dispatch_rfid(self, uid):
        active_frame = self.frames.get(self.current_frame_name)
        
        # DEBUG: Let's see what's actually happening in the console
        print(f"--- RFID DETECTED ---")
        print(f"UID: {uid}")
        print(f"Current Frame: {self.current_frame_name}")
        
        if not active_frame: 
            print("Debug: Active frame object not found in dictionary.")
            return

        # Use hasattr to check if the frame is READY to receive data
        if hasattr(active_frame, "handle_rfid_tap"):
            print(f"Success: Calling handle_rfid_tap on {self.current_frame_name}")
            active_frame.handle_rfid_tap(uid)
        elif hasattr(active_frame, "handle_rfid_scan"):
            print(f"Success: Calling handle_rfid_scan on {self.current_frame_name}")
            active_frame.handle_rfid_scan(uid)
        else:
            print(f"Warning: {self.current_frame_name} is active but has no RFID handler function.")

    # Check for the specific methods regardless of the class name

    def login_success(self, user_data):
        self.current_user = user_data  
        for FrameClass in (
            MainDashboard, StudentRecord, TeacherRecord,
            FetcherRecord, RfidRegistration, RFIDHistory,
            Report, Account, ClassroomFrame, OverrideFrame
        ):
            frame = FrameClass(self.container, self)
            self.frames[FrameClass.__name__] = frame
            frame.place(relwidth=1, relheight=1)
        self.show_frame("MainDashboard")

    def logout(self):
        self.current_user = None 
        for name in list(self.frames.keys()):
            if name not in ["LoginFrame", "SignUpFrame", "ForgotPasswordFrame"]:
                self.frames[name].destroy()
                del self.frames[name]
        self.show_frame("LoginFrame")

    def on_closing(self):
        self.running = False
        self.destroy()

if __name__ == "__main__":
    app = Rfid()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()