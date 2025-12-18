import tkinter as tk
from tkinter import messagebox



class report(tk.Frame):
    def __init__ (self, root):
        super().__init__(root, bg="#b2e5ed")
        self.root = root

        root.title("RFID MANAGEMENT SYSTEM - REPORT")
        root.geometry("1350x700+0+0")
            