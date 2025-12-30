import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import ImageTk, Image
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.database import db_connect


class Student(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg="#b2e5ed")
        self.root = root

        root.title("RFID MANAGEMENT SYSTEM - STUDENT RECORD")
        root.geometry("1350x700+0+0")

        self.pack(fill="both", expand=True)

        # ================= HEADER =================
        header = tk.Frame(self, height=95, bg="#0047AB", bd=2, relief="groove")
        header.pack(fill="x")

        tk.Label(
            header,
            text="STUDENT INFORMATION",
            font=("Arial", 24, "bold"),
            bg="#0047AB",
            fg="white"
        ).place(x=50, y=25)

        # ================= LEFT PANEL =================
        self.student_left = tk.Frame(self, width=500, height=550, bg="white", bd=2, relief="groove")
        self.student_left.place(x=50, y=125)
        self.student_left.pack_propagate(False)

        # ================= PHOTO =================
        self.photo_frame = tk.Frame(self.student_left, width=200, height=200, bg="#E0E0E0", bd=2, relief="ridge")
        self.photo_frame.place(x=20, y=20)

        self.photo_label = tk.Label(self.photo_frame, bg="#E0E0E0")
        self.photo_label.pack(fill="both", expand=True)

        tk.Button(self.student_left, text="Upload Photo", command=self.upload_photo)\
            .place(x=60, y=240)

        # ================= VARIABLES =================
        self.student_name_var = tk.StringVar()
        self.grade_var = tk.StringVar()
        self.student_id_var = tk.StringVar()
        self.guardian_name_var = tk.StringVar()
        self.guardian_contact_var = tk.StringVar()
        self.teacher_name_var = tk.StringVar()

        fields = [
            ("Full Name", self.student_name_var),
            ("Grade Level", self.grade_var),
            ("Student ID", self.student_id_var),
            ("Guardian Name", self.guardian_name_var),
            ("Guardian Contact", self.guardian_contact_var),
            ("Teacher Name", self.teacher_name_var)
        ]

        y = 290
        for i, (label, var) in enumerate(fields):
            tk.Label(self.student_left, text=label, bg="white", font=("Arial", 12))\
                .place(x=20, y=y + i * 40)
            tk.Entry(self.student_left, textvariable=var, font=("Arial", 12), width=30)\
                .place(x=160, y=y + i * 40)

        # ================= BUTTONS =================
        tk.Button(self.student_left, text="ADD", bg="#4CAF50", fg="white",
                  command=self.add_student).place(x=40, y=510)

        tk.Button(self.student_left, text="EDIT", bg="#2196F3", fg="white",
                  command=self.edit_student).place(x=180, y=510)

        tk.Button(self.student_left, text="DELETE", bg="#F44336", fg="white",
                  command=self.delete_student).place(x=320, y=510)

        # ================= RIGHT PANEL =================
        self.right_panel = tk.Frame(self, width=550, height=500, bg="white", bd=2, relief="groove")
        self.right_panel.place(x=700, y=150)

        tk.Label(self.right_panel, text="Search Student", font=("Arial", 16, "bold"), bg="white")\
            .place(x=20, y=20)

        self.search_student_var = tk.StringVar()
        tk.Entry(self.right_panel, textvariable=self.search_student_var, width=25)\
            .place(x=20, y=60)

        tk.Button(self.right_panel, text="Search", command=self.search_student)\
            .place(x=300, y=57)

        # ================= TABLE =================
        columns = ("id", "name", "grade")
        self.student_table = ttk.Treeview(self.right_panel, columns=columns, show="headings", height=12)

        for col, text in zip(columns, ["Student ID", "Full Name", "Grade"]):
            self.student_table.heading(col, text=text)
            self.student_table.column(col, width=160)

        self.student_table.place(x=20, y=140, width=500)

        self.load_data()

    # ================= FUNCTIONS =================
    def upload_photo(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            img = Image.open(file_path).resize((200, 200))
            self.photo = ImageTk.PhotoImage(img)
            self.photo_label.config(image=self.photo)
            self.photo_label.image = self.photo

    def load_data(self):
        self.student_table.delete(*self.student_table.get_children())

        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT Student_id, Student_name, grade_lvl FROM student")
            for row in cursor.fetchall():
                self.student_table.insert("", "end", values=row)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def add_student(self):
        if not all([
            self.student_name_var.get(),
            self.student_id_var.get(),
            self.grade_var.get(),
            self.guardian_name_var.get(),
            self.guardian_contact_var.get(),
            self.teacher_name_var.get()
        ]):
            messagebox.showerror("Error", "All fields are required")
            return

        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO student
                (Student_name, Student_id, grade_lvl, Guardian_name, Guardian_contact, Teacher_name)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                self.student_name_var.get(),
                self.student_id_var.get(),
                self.grade_var.get(),
                self.guardian_name_var.get(),
                self.guardian_contact_var.get(),
                self.teacher_name_var.get()
            ))
            conn.commit()
            self.load_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Student added successfully")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def edit_student(self):
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE student SET
                Student_name=%s, grade_lvl=%s,
                Guardian_name=%s, Guardian_contact=%s, Teacher_name=%s
                WHERE Student_id=%s
            """, (
                self.student_name_var.get(),
                self.grade_var.get(),
                self.guardian_name_var.get(),
                self.guardian_contact_var.get(),
                self.teacher_name_var.get(),
                self.student_id_var.get()
                messagebox))
            conn.commit()
            self.load_data()
            self.clear_fields()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def delete_student(self):
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM student WHERE Student_id=%s",
                           (self.student_id_var.get(),))
            messagebox.showinfo("Success", "Student deleted successfully")
            conn.commit()
            self.load_data()
            self.clear_fields()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def clear_fields(self):
        for var in [
            self.student_name_var,
            self.student_id_var,
            self.grade_var,
            self.guardian_name_var,
            self.guardian_contact_var,
            self.teacher_name_var
        ]:
            var.set("")

    def search_student(self):
        keyword = self.search_student_var.get()
        self.student_table.delete(*self.student_table.get_children())

        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Student_id, Student_name, grade_lvl
                FROM student
                WHERE Student_name LIKE %s
            """, (f"%{keyword}%",))
            for row in cursor.fetchall():
                self.student_table.insert("", "end", values=row)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = Student(root)
    root.mainloop()
