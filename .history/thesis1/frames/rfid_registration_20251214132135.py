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

        #left fetchcer information 
        width = 400
        height = 500
        self.fetcher_frame = tk.Frame(self, width=width, height=height, bg="white", bd=2, relief="groove")
        self.fetcher_frame.place(x=675 + (675 - width)//2, y=(700 - height)//2)
        self.fetcher_frame.pack_propagate(False)

        title = tk.Label(self.fetcher_frame, text="FETCHER INFORMATION", font=("Arial", 24, "bold"), bg="white", fg="#0047AB")
        title.pack(pady=10)

        tk.Label(self.fetcher_frame, text="Name:", bg="white").pack()
        self.name_label = tk.Label(self.fetcher_frame, text="", bg="white")
        self.name_label.pack()

        tk.Label(self.fetcher_frame, text="RFID:", bg="white").pack()
        self.rfid_label = tk.Label(self.fetcher_frame, text="", bg="white")
        self.rfid_label.pack()

        tk.Label(self.fetcher_frame, text="Address:", bg="white").pack()
        self.email_label = tk.Label(self.fetcher_frame, text="", bg="white")
        self.email_label.pack()

        tk.Label(self.fetcher_frame, text="Phone Number:", bg="white").pack()
        self.phone_label = tk.Label(self.fetcher_frame, text="", bg="white")
        self.phone_label.pack()

        # right student info

        

