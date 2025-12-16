import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import os
from tkinter import filedialog

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
            height=95,
            bg="blue",
            bd=2,
            relief="groove"
        )
        self.student_frame.pack(fill="both")
        
        tk.Label (self.student_frame, text="STUDENT INFORMATION", font=("Arial", 24, "bold"), bg="white", fg="#0047AB").place(x=50, y=25)
        

        #student box left  
        self.student_left = tk.Frame(self,width=500, height = 500, bg = "white", bd="1.5", relief = "groove")
        self.student_left.place (x = 50, y = 150)
        self.student_left.pack_propagate(False)

         #photo 
        self.photo_frame = tk.Frame(self.student_left, width=300, height=3, bg="white", bd=2, relief="groove")
        self.photo_frame.place(x=20, y=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = Student(root)
    root.mainloop()
