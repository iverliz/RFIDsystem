import tkinter as tk
from tkinter import messagebox



class report(tk.Frame):
    def __init__ (self, root):
        super().__init__(root, bg="#b2e5ed")
        self.root = root

        root.title("RFID MANAGEMENT SYSTEM - REPORT")
        root.geometry("1350x700+0+0")
        self.pack(fill="both", expand=True)


        self.report_frame = tk.Frame(self, width=450, height=350, bg="white", bd=2, relief="groove")
        self.report_frame.place(x=60, y=90)    