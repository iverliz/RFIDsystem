import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from PIL import ImageTk, Image
from datetime import datetime
from frames.rfid_registration import RfidRegistration
from frames.login import App
from.frames.main_dashboard import MainDashboard
from.frames.history_log import HistoryLog
from frames.report import Report
from.frames.account import Account
fro

class Rfid(tk.Tk):
    def __init__(self):
        super().__init__()   # initialize Tk properly

        self.title("RFID MANAGEMENT SYSTEM")
        self.geometry("1350x700+0+0")

        frame = RfidRegistration(self)
        frame.pack(fill="both", expand=True)



if __name__ == "__main__":
    app = Rfid()
    app.mainloop()


