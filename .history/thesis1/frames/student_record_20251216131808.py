import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import os


class student(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg="#F5F5F5")
        self.parent = parent
        

        self.student_frame = tk.Frame(self, width=450, height=350, bg="white", bd=2, relief="groove")

        tk.Label(self.student_frame, text="STUDENT INFORMATION", font=("Arial", 24, "bold"), bg="white", fg="#0047AB").place(x=20, y=20)
        




if __name__ == "__main__":
    


