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
from frames.teacher_record import TeacherRecord
from.frames.student_record import StudentRecord
from frames.fetcher_record import FetcherRecord


class Rfid(tk.Tk):
    def __init__(self):
        super().__init__()   # initialize Tk properly

        self.title("RFID MANAGEMENT SYSTEM")
        self.geometry("1350x700+0+0")

        frame = RfidRegistration(self)
        frame.pack(fill="both", expand=True)

        self.frames = {}
        for F in (App, MainDashboard, HistoryLog, Report, Account, TeacherRecord, StudentRecord, FetcherRecord):
            frame = F(self)
            self.frames[F.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("App")



if __name__ == "__main__":
    app = Rfid()
    app.mainloop()


