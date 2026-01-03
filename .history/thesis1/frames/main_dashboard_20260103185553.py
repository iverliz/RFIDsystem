class MainDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.configure(bg="#b2e5ed")
        # self.pack(fill="both", expand=True)  <-- REMOVE THIS LINE

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

        # ================= DEFAULT PAGE =================
        self.open_frame(StudentRecord)
