import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import os


class student(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg="#F5F5F5")
        self.parent = parent
        

        self.student_frame = tk.Frame(self, width=1350, height=700, bg="#E0E0E0")
        self.student_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.student_frame.pack_propagate(False)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_dir, "..", "assets", "icon", "ccclogo.jpg")
        image_path = os.path.normpath(image_path)
        try:
            image = Image.open(image_path)
            image = image.resize((675, 700))
            self.photo = ImageTk.PhotoImage(image)
            label = tk.Label(self.student_frame, image=self.photo, bg="#E0E0E0")
            label.pack(fill=tk.BOTH, expand=True)
        except FileNotFoundError:
            tk.Label(self.student_frame, text="Image not found", bg="gray", fg="white").pack(fill=tk.BOTH, expand=True) 