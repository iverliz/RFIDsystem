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
        self.create_menu_button