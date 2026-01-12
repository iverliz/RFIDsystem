import tkinter as tk 
import os 
import sys


BIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BIN_DIR)

from utils.database import db_connect

class EnrollThisYear(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        #header 
        header = tk.Frame(self, height=70, bg="#0047AB")
        header.pack(fill = "x")


        #header  style 
        tk.Label(
            header, text="ENROLL THIS YEAR", font=("Arial", 20, "bold"), bg="#0047AB", fg="white"
        ).place(x=30, y=18)
        
        


        

