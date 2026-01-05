import tkinter as tk
import os

from frames.history_log import RFIDHistory
from frames.report import Report
from frames.account import Account
from frames.teacher_record import TeacherRecord
from frames.student_record import StudentRecord
from frames.fetcher_record import FetcherRecord
from frames.rfid_registration import RfidRegistration

SESSION_FILE = "session.txt"


class MainDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.configure(bg="#b2e5ed")
        self.pack(fill="both", expand=True)

        # ================= CURRENT PAGE =================
        self.current_frame = None

        # ================= SIDEBAR =================
        self.sidebar = tk.Frame(self, width=250, bg="#87dfe9")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        self.create_menu_button("Student Record", StudentRecord)
        self.create_menu_button("Teacher Record", TeacherRecord)
        self.create_menu_button("Fetcher Record", FetcherRecord)
        self.create_menu_button("RFID Registration", RfidRegistration)
        self.create_menu_button("History Log", RFIDHistory)
        self.create_menu_button("Account Settings", Account)
        self.create_menu_button("Reports", Report)

        # ================= MAIN AREA =================
        self.main_area = tk.Frame(self, bg="#b2e5ed")
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ================= TOP BAR =================
        self.topbar = tk.Frame(self.main_area, height=50, bg="#2ec7c0")
        self.topbar.pack(fill="x")

        tk.Button(
            self.topbar,
            text="Logout",
            bg="#ff6b6b",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.logout 
        ).pack(side="right", padx=20, pady=10)

        
        self.open_frame(StudentRecord)

    
    def open_frame(self, frame_class):
        if self.current_frame is not None:
            self.current_frame.destroy()

       
        self.current_frame = frame_class(self.main_area, self.controller)
        self.current_frame.pack(fill="both", expand=True)

    
    def create_menu_button(self, text, frame_class):
        tk.Button(
            self.sidebar,
            text=text,
            bg="#2ec7c0",
            fg="white",
            anchor="w",
            relief="flat",
            padx=10,
            pady=5,
            font=("Arial", 12, "bold"),
            command=lambda: self.open_frame(frame_class)
        ).pack(fill="x", pady=2)

    # ================= LOGOUT =================
    def logout(self):
        # Remove session file
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)

        # Clear login fields
        login_frame = self.controller.frames["LoginFrame"]
        login_frame.username.delete(0, tk.END)
        login_frame.password.delete(0, tk.END)

        # Go back to login screen
        self.controller.show_frame("LoginFrame")
