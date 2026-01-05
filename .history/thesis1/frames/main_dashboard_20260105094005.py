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
        self.configure(bg="#e0f7fa")
        self.pack(fill="both", expand=True)

        # ================= CURRENT PAGE =================
        self.current_frame = None

        # ================= SIDEBAR =================
        self.sidebar = tk.Frame(self, width=250, bg="#00acc1")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Logo or App Title
        tk.Label(
            self.sidebar,
            text="RFID MANAGEMENT",
            bg="#00acc1",
            fg="white",
            font=("Arial", 16, "bold")
        ).pack(pady=20)

        self.create_menu_button("Student Record", StudentRecord)
        self.create_menu_button("Teacher Record", TeacherRecord)
        self.create_menu_button("Fetcher Record", FetcherRecord)
        self.create_menu_button("RFID Registration", RfidRegistration)
        self.create_menu_button("History Log", RFIDHistory)
        self.create_menu_button("Account Settings", Account)
        self.create_menu_button("Reports", Report)

        # ================= MAIN AREA =================
        self.main_area = tk.Frame(self, bg="#e0f7fa")
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ================= TOP BAR =================
        self.topbar = tk.Frame(self.main_area, height=50, bg="#26c6da", bd=2, relief="groove")
        self.topbar.pack(fill="x")

        tk.Label(
            self.topbar,
            text="Dashboard",
            bg="#26c6da",
            fg="white",
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=20)

        logout_btn = tk.Button(
            self.topbar,
            text="Logout",
            bg="#ff6b6b",
            fg="white",
            font=("Arial", 12, "bold"),
            relief="raised",
            bd=2,
            padx=15,
            pady=5,
            command=self.logout
        )
        logout_btn.pack(side="right", padx=20, pady=8)

        # ================= OPEN DEFAULT FRAME =================
        self.open_frame(StudentRecord)

    # ================= OPEN FRAMES =================
    def open_frame(self, frame_class):
        if self.current_frame is not None:
            self.current_frame.destroy()

        self.current_frame = frame_class(self.main_area, self.controller)
        self.current_frame.pack(fill="both", expand=True)

    # ================= MENU BUTTON =================
    def create_menu_button(self, text, frame_class):
        btn = tk.Button(
            self.sidebar,
            text=text,
            bg="#00acc1",
            fg="white",
            anchor="w",
            relief="flat",
            padx=20,
            pady=15,
            font=("Arial", 12, "bold"),
            command=lambda: self.open_frame(frame_class)
        )
        btn.pack(fill="x", pady=2)

        # Hover effect
        btn.bind("<Enter>", lambda e: btn.config(bg="#00838f"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#00acc1"))

    # ================= LOGOUT FUNCTION =================
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
