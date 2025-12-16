import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import os


class Student(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg="#b2e5ed")  # ✅ FIXED
        self.root = root

        root.title("RFID MANAGEMENT SYSTEM - STUDENT RECORD")
        root.geometry("1350x700+0+0")

        self.pack(fill="both", expand=True)

        # ================= STUDENT FRAME =================
        self.student_frame = tk.Frame(
            self,
            width=450,
            height=100,
            bg="blue",
            bd=2,
            relief="groove"
        )
        self.student_frame.pack(fill="both")
        
        tk.Label (self.student_frame, text="STUDENT INFORMATION", font=("Arial", 24, "bold"), bg="white", fg="#0047AB").place(x=20, y=)


if __name__ == "__main__":
    root = tk.Tk()
    app = Student(root)
    root.mainloop()
