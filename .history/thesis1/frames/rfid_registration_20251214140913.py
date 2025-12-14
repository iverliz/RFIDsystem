import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk


class RfidRegistration(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg="#b2e5ed")
        self.root = root

        root.title("RFID MANAGEMENT SYSTEM - RFID REGISTRATION")
        root.geometry("1350x700+0+0")

        self.pack(fill="both", expand=True)

        # ================= SEARCH BAR =================
        self.search_var = tk.StringVar()

        search_frame = tk.Frame(self, bg="#b2e5ed")
        search_frame.pack(pady=10)

        tk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side="left", padx=5)
        tk.Button(search_frame, text="Search", command=self.search).pack(side="left")

       
        

if __name__ == "__main__":
    root = tk.Tk()
    app = RfidRegistration(root)
    root.mainloop()
