import tkinter as tk 
from tkinter import ttk, messagebox, simpledialog



class RfidRegistration(tk.tk):
    def __init__(self, root):
        super().__init__(root)
        self.title("RFID MANGEMENT SYSTEM - RFID REGISTRATION")
        self.geometry("1350x700+0+0")
        self.configure(bg="#b2e5ed")