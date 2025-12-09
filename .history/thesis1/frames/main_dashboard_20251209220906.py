import tkinter as tk 
import PIL as pillow
from PIL import ImageTk, Image

class MainDashboard(tk.Tk):
    def __init__(self, parent):
        super().__init__()
        self.title("RFID MANAGEMENT SYSTEM - DASHBORAD")
        self.geometry("1350x700+0+0")
        self.configure(bg="9ABDDC")

        self.sidebar  = tk.Frame(self, width=675, height=700, bg="#E0E0E0")
        self.sidebar.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.sidebar.pack_propagate(False)

        self.create_mune_button("Student record")
        self.create_menu_button("Teacher record")
        self.create_menu_button("Fetcher record")
        self.create_menu_button("RFID Registration")
        self.create_menu_button("History Log")
        self.create_menu_button("Account Settings")
        self.create_menu_button("Reports")

        self.topbar = tk.Frame(self.main_area, height=50, bg="#0047AB")
        self.topbar.pack(fill="x", side = "top")

        logout_button = tk.Button(self.topbar, text="Logout", bg="#D9534F",activebackground=, fg="#F5F5F5", font=("Arial", 12, "bold"), command=self.logout)
        logout_button.place(x=1170, y=10)