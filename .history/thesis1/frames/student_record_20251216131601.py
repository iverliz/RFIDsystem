import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import os


class student(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg="#F5F5F5")
        self.parent = parent
        

        self.student_