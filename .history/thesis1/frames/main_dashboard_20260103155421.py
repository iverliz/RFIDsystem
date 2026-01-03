import tkinter as tk


class MainDashboard(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.configure(bg="#b2e5ed")  # main background

        # --- SIDEBAR ---
        self.sidebar = tk.Frame(self, width=250, bg="#87dfe9")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # MENU BUTTONS
        self.create_menu_button("Student Record")
        self.create_menu_button("Teacher Record")
        self.create_menu_button("Fetcher Record")
        self.create_menu_button("RFID Registration")
        self.create_menu_button("History Log")
        self.create_menu_button("Account Settings")
        self.create_menu_button("Reports")

        # --- MAIN AREA ---
        self.main_area = tk.Frame(self, bg="#b2e5ed")
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- TOP BAR ---
        self.topbar = tk.Frame(self.main_area, height=50, bg="#2ec7c0")
        self.topbar.pack(fill="x", side="top")

        # LOGOUT BUTTON
        logout_button = tk.Button(
            self.topbar,
            text="Logout",
            bg="#ff6b6b",
            activebackground="#ff5252",
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            font=("Arial", 12, "bold"),
            command=self.logout
        )
        logout_button.pack(side="right", padx=20, pady=10)

    # -----------------------
    # Create Sidebar Buttons
    # -----------------------
    def create_menu_button(self, text):
        btn = tk.Button(
            self.sidebar,
            text=text,
            bg="#2ec7c0",
            fg="white",
            activebackground="#99dde7",
            activeforeground="white",
            anchor="w",
            relief="flat",
            padx=20,
            pady=15,
            font=("Arial", 12, "bold")
        )
        btn.pack(fill="x", pady=2)

    # -----------------------
    # Logout Function
    # -----------------------
    def logout(self):
        self.parent.logout()
