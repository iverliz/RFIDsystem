import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import os


class student(tk.Frame):
    def __init__(self, root):
        super().__init__(self, root)
        self,root = root
        self.configure(bg="#b2e5ed")
        root.title("RFID MANAGEMENT SYSTEM - STUDENT RECORD")
        root.geometry("1350x700+0+0")
        self.propagate(False)
        

        self.student_frame = tk.Frame(self, width=450, height=350, bg="white", bd=2, relief="groove")

        tk.Label(self.student_frame, text="STUDENT INFORMATION", font=("Arial", 24, "bold"), bg="white", fg="#0047AB").place(x=20, y=20)
        




if __name__ == "__main__":
    root = tk.Tk()
    app = student(root)
    root.mainloop()


