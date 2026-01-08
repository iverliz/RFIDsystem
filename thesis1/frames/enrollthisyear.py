import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

BIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BIN_DIR)

from utils.database import db_connect  # optional for later use


class EnrollThisYear(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # ================= HEADER =================
        header = tk.Frame(self, height=70, bg="#0047AB")
        header.pack(fill="x")

        tk.Label(
            header,
            text="ENROLL THIS YEAR",
            font=("Arial", 20, "bold"),
            bg="#0047AB",
            fg="white"
        ).place(x=30, y=18)

        # ================= CONTENT =================
        content = tk.Frame(self, padx=40, pady=30)
        content.pack(fill="both", expand=True)

        # Student Name
        tk.Label(content, text="Student Name", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = tk.Entry(content, width=30)
        self.name_entry.grid(row=0, column=1, pady=5)

        # Grade
        tk.Label(content, text="Grade Level", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
        self.grade_combo = ttk.Combobox(
            content,
            values=["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5"],
            state="readonly",
            width=27
        )
        self.grade_combo.grid(row=1, column=1, pady=5)
        self.grade_combo.current(0)

        # School Year
        tk.Label(content, text="School Year", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=5)
        self.year_entry = tk.Entry(content, width=30)
        self.year_entry.insert(0, "2025 - 2026")
        self.year_entry.grid(row=2, column=1, pady=5)

        # Buttons
        btn_frame = tk.Frame(content, pady=20)
        btn_frame.grid(row=3, column=0, columnspan=2)

        tk.Button(
            btn_frame,
            text="Enroll Student",
            bg="#0047AB",
            fg="white",
            font=("Arial", 11, "bold"),
            width=15,
            command=self.enroll_student
        ).pack(side="left", padx=10)

        tk.Button(
            btn_frame,
            text="Clear",
            width=10,
            command=self.clear_form
        ).pack(side="left")

    # ================= ACTIONS =================
    def enroll_student(self):
        name = self.name_entry.get()
        grade = self.grade_combo.get()
        year = self.year_entry.get()

        if not name:
            messagebox.showwarning("Missing Data", "Please enter student name.")
            return

        # Prototype behavior
        messagebox.showinfo(
            "Enrollment Successful",
            f"{name} enrolled in {grade}\nSchool Year: {year}"
        )

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.grade_combo.current(0)
        self.year_entry.delete(0, tk.END)
        self.year_entry.insert(0, "2025 - 2026")
