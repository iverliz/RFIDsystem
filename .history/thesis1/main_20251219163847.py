import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from PIL import ImageTk, Image
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

from datetime import datetime
from frames.login import LoginSystem 

from utils.database import db_connect



class Rfid(tk.Tk):
    def __init__(self, root):
        self.root = root
        self.root.title("RFID MANAGEMENT SYSTEM")
        self.root.geometry("1350x700+0+0")

        
          # Load login page into main window
        login_frame = LoginSystem(self.root)
        login_frame.pack(fill="both", expand=True)



if __name__ == "__main__":
    root = tk.Tk()
    obj = Rfid(root)
    root.mainloop()


