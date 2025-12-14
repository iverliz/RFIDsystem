import tkinter as tk 
from tkinter import ttk, messagebox, simpledialog



class RfidRegistration(tk.tk):
    def __init__(self, root):
        super().__init__(root)
        self.title("RFID MANGEMENT SYSTEM - RFID REGISTRATION")
        self.geometry("1350x700+0+0")
        self.configure(bg="#b2e5ed")

        search_var = tk.StringVar()
        search_entry = tk.Entry(self, textvariable=search_var, width=30)
        search_entry.pack(pady=20)

        search_button = tk.Button(self, text="Search", command=lambda: self.search(search_var.get()))
        search_button.pack()

        self.student