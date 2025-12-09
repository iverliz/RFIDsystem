import tkinter as tk 
import PIL as pillow
from PIL import ImageTk, Image

class MainDashboard(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller