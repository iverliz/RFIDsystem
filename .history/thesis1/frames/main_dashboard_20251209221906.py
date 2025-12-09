import tkinter as tk


class MainDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RFID MANAGEMENT SYSTEM - DASHBOARD")
        self.geometry("1350x700+0+0")
        self.configure(bg="#9ABDDC")

        # --- SIDEBAR ---
        self.sidebar = tk.Frame(self, width=250, bg="#E0E0E0")
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
        self.main_area = tk.Frame(self, bg="#F5F5F5")
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- TOP BAR ---
        self.topbar = tk.Frame(self.main_area, height=50, bg="#0047AB")
        self.topbar.pack(fill="x", side="top")

        # LOGOUT BUTTON
        logout_button = tk.Button(
            self.topbar,
            text="Logout",
            bg="#D9534F",
            activebackground="#C9302C",
            activeforeground="#F5F5F5",
            fg="#F5F5F5",
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
            bg="#1E1E1E",
            fg="#F5F5F5",
            activebackground="#333333",
            activeforeground="#F5F5F5",
            anchor="w",
            relief="flat",
            padx=20,
            pady=15,
            font=("Arial", 12, "bold")
        )
        btn.pack(fill="x")

    # -----------------------
    # Logout Function
    # -----------------------
    def logout(self):
        self.destroy()


if __name__ == "__main__":
    app = MainDashboard()
    app.mainloop()
