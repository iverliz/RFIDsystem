import tkinter as tk 
import PIL as pillow
from PIL import ImageTk, Image

class MainDashboard(tk.Tk):
    def __init__(self, parent):
        super().__init__()
        self.title("RFID MANAGEMENT SYSTEM - DASHBORAD")
        self.geometry("1350x700+0+0")
        self.configure(bg="9ABDDC")

        self.create_mune_button("Student record")
        self.create_

