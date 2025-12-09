import tkinter as tk 
import PIL as pillow
from PIL import ImageTk, Image

class MainDashboard(tk.Tk):
    def __init__(self, parent, controller):
        super().__init__()
        self.controller = controller
        

