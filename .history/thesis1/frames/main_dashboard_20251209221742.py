import tkinter as tk

class MainDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RFID MANAGEMENT SYSTEM - DASHBOARD")
        self.geometry("1350x700+0+0")
        self.configure(bg="#9ABDDC")

        # --- SIDEBAR ---
        self.sidebar = tk.Frame(self, width=220, bg="#E0E0E0")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Sidebar Buttons
        self.create_menu_button("Student Record")
        self.create_menu_button("Teacher Record")
        self.create_menu_button("Fetcher Record")
        self.create_menu_button("RFID Registration")
        self.create_menu_button("History Log")
        self.create_menu_button("Account Settings")
        self.create_menu_button("Reports")

        # --- MAIN AREA ---
        self.main_area = tk.Frame(self, bg="#F5F5F5")
        self.main_area.pack(side="left", fill="both", expand=True)

        # --- TOP BAR ---
        self.topbar = tk.Frame(self.main_area, height=50, bg="#0047AB")
        self.topbar.pack(fill="x", side="top")

        # Logout Button (Top Right)
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

    # --------------------------------------------------------
    # Sidebar Menu Button
    # --------------------------------------------------------
    def create_menu_button(self, text):
        btn = tk.Button(
            self.sidebar,
            text=text,
            bg="#1E1E1E",
            activebackground="#333333",
            activeforeground="#F5F5F5",
            fg="#F5F5F5",
            anchor="w",
            relief="flat",
            padx=20,
            pady=15,
            font=("Arial", 12, "bold"),
            command=lambda: self.load_page(text)
        )
        btn.pack(fill="x")

    # --------------------------------------------------------
    # Logout
    # --------------------------------------------------------
    def logout(self):
        self.destroy()

    # --------------------------------------------------------
    # Placeholder for page content (you can expand later)
    # --------------------------------------------------------
    def load_page(self, name):
        for widget in self.main_area.winfo_children():
            if widget != self.topbar:
                widget.destroy()

        tk.Label(
            self.main_area,
            text=f"{name} Page Loaded",
            font=("Arial", 20, "bold"),
            bg="#F5F5F5"
        ).pack(pady=80)


if __name__ == "__main__":
    app = MainDashboard()
    app.mainloop()
