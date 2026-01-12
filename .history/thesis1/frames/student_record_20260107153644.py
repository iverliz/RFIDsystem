import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import ImageTk, Image
import os
import sys
import time

# ================= PATH SETUP =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.database import db_connect

PHOTO_DIR = os.path.join(BASE_DIR, "student_photos")
os.makedirs(PHOTO_DIR, exist_ok=True)


class StudentRecord(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#b2e5ed")
        self.controller = controller
        self.photo_path = None
        self.selected_student_id = None

        # ================= HEADER =================
        header = tk.Frame(self, height=70, bg="#0047AB")
        header.pack(fill="x")

        tk.Label(
            header,
            text="STUDENT INFORMATION",
            font=("Arial", 20, "bold"),
            bg="#0047AB",
            fg="white"
        ).place(x=30, y=18)

        # ================= LEFT PANEL =================
        self.left_box = tk.Frame(self, width=430, height=460, bg="white", bd=2, relief="groove")
        self.left_box.place(x=40, y=90)
        self.left_box.pack_propagate(False)

        # ================= PHOTO =================
        self.photo_frame = tk.Frame(self.left_box, width=160, height=160, bg="#E0E0E0", bd=2, relief="ridge")
        self.photo_frame.place(x=20, y=20)
        self.photo_frame.pack_propagate(False)

        self.photo_label = tk.Label(self.photo_frame, bg="#E0E0E0")
        self.photo_label.pack(fill="both", expand=True)

        tk.Button(
            self.left_box,
            text="Upload Photo",
            width=14,
            command=self.upload_photo
        ).place(x=210, y=80)

        # ================= VARIABLES =================
        self.student_name_var = tk.StringVar()
        self.grade_var = tk.StringVar()
        self.student_id_var = tk.StringVar()
        self.guardian_name_var = tk.StringVar()
        self.guardian_contact_var = tk.StringVar()
        self.teacher_name_var = tk.StringVar()

        # ================= FORM =================
        fields = [
            ("Full Name:", self.student_name_var),
            ("Grade:", self.grade_var),
            ("Student ID:", self.student_id_var),
            ("Guardian Name:", self.guardian_name_var),
            ("Guardian Contact:", self.guardian_contact_var),
            ("Teacher Name:", self.teacher_name_var),
        ]

        y = 200
        for i, (label, var) in enumerate(fields):
            tk.Label(
                self.left_box,
                text=label,
                bg="white",
                font=("Arial", 11)
            ).place(x=20, y=y + i * 35)

            tk.Entry(
                self.left_box,
                textvariable=var,
                width=30,
                font=("Arial", 11)
            ).place(x=150, y=y + i * 35)

        # ================= BUTTONS =================
        btn_frame = tk.Frame(self.left_box, bg="white")
        btn_frame.place(x=40, y=410)

        tk.Button(
            btn_frame,
            text="ADD",
            width=10,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.add_student
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            btn_frame,
            text="EDIT",
            width=10,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.edit_student
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            btn_frame,
            text="DELETE",
            width=10,
            bg="#F44336",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.delete_student
        ).grid(row=0, column=2, padx=5)

        # ================= RIGHT PANEL =================
        self.right_panel = tk.Frame(self, width=500, height=460, bg="white", bd=2, relief="groove")
        self.right_panel.place(x=520, y=90)
        self.right_panel.pack_propagate(False)

        tk.Label(
            self.right_panel,
            text="Search Student",
            font=("Arial", 14, "bold"),
            bg="white"
        ).place(x=20, y=15)

        self.search_var = tk.StringVar()
        tk.Entry(self.right_panel, textvariable=self.search_var, width=25, font=("Arial", 11))\
            .place(x=20, y=50)

        tk.Button(
            self.right_panel,
            text="Search",
            command=self.search_student
        ).place(x=260, y=47)

        self.count_var = tk.StringVar(value="Total Students: 0")
        tk.Label(
            self.right_panel,
            textvariable=self.count_var,
            font=("Arial", 11, "bold"),
            fg="#0047AB",
            bg="white"
        ).place(x=20, y=85)

        # ================= TABLE =================
        self.student_table = ttk.Treeview(
            self.right_panel,
            columns=("Student_id", "Student_name", "grade_lvl"),
            show="headings",
            height=12
        )

        self.student_table.heading("Student_id", text="Student ID")
        self.student_table.heading("Student_name", text="Full Name")
        self.student_table.heading("grade_lvl", text="Grade")

        self.student_table.column("Student_id", width=120)
        self.student_table.column("Student_name", width=220)
        self.student_table.column("grade_lvl", width=80)

        self.student_table.place(x=20, y=120, width=450)
        self.student_table.bind("<<TreeviewSelect>>", self.on_table_select)

        self.load_data()

    # ================= FUNCTIONS =================
    def upload_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if path:
            img = Image.open(path).resize((160, 160))
            self.photo = ImageTk.PhotoImage(img)
            self.photo_label.config(image=self.photo)
            self.photo_label.image = self.photo
            self.photo_path = path

        

    def student_id_exists(self, student_id):
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM student WHERE Student_id=%s", (student_id,))
            return cursor.fetchone() is not None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def load_data(self):
        self.student_table.delete(*self.student_table.get_children())
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT Student_id, Student_name, grade_lvl FROM student")
            rows = cursor.fetchall()
            for row in rows:
                self.student_table.insert("", "end", values=row)
            self.count_var.set(f"Total Students: {len(rows)}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def search_student(self):
        keyword = self.search_var.get()
        self.student_table.delete(*self.student_table.get_children())

        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Student_id, Student_name, grade_lvl FROM student WHERE Student_name LIKE %s",
            (f"%{keyword}%",)
        )
        rows = cursor.fetchall()
        for row in rows:
            self.student_table.insert("", "end", values=row)
        self.count_var.set(f"Total Students: {len(rows)}")
        cursor.close()
        conn.close()

    def validate(self):
        if not self.student_id_var.get().strip():
            return "Student ID is required"
        if not self.grade_var.get().isdigit():
            return "Grade must be a number or please input grade level of the student e.g 1, 2, 3, 4, 5, 6"
        if not self.student_id_var.get().isdigit():
            return "please input student ID as a number"
        if not self .student_name_var.get().strip():
            return "Student Name is required"
        if not self.guardian_name_var.get().strip():
            return "Guardian Name is required"
        if not self.guardian_contact_var.get().strip():
            return "Guardian Contact is required"
        if not self.teacher_name_var.get().strip():
            return "Teacher Name is required"
    def add_student(self):
        if not self.photo_path:
            messagebox.showerror("Error", "Photo is required")
            return

        try:
            student_id = int(self.student_id_var.get())
            grade = int(self.grade_var.get())

            if self.student_id_exists(student_id):
                messagebox.showerror("Error", "Student ID already exists")
                return

            img_save = os.path.join(PHOTO_DIR, f"student_{student_id}_{int(time.time())}.jpg")
            Image.open(self.photo_path).save(img_save)

            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO student
                (Student_name, Student_id, grade_lvl, Guardian_name,
                 Guardian_contact, Teacher_name, photo_path)
                VALUES (%s,%s,%s,%s,%s,%s,%s)""", (
                self.student_name_var.get(),
                student_id,
                grade,
                self.guardian_name_var.get(),
                self.guardian_contact_var.get(),
                self.teacher_name_var.get(),
                img_save
            ))
            conn.commit()

            self.load_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Student added successfully")

            error = self.validate()
            if error:
                messagebox.showerror("Error", error)    

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def edit_student(self):
        try:
            student_id = int(self.student_id_var.get())
            grade = int(self.grade_var.get())

            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""UPDATE student SET
                    Student_name=%s,
                    grade_lvl=%s,
                    Guardian_name=%s,
                    Guardian_contact=%s,
                    Teacher_name=%s
                WHERE Student_id=%s""", (
                self.student_name_var.get(),
                grade,
                self.guardian_name_var.get(),
                self.guardian_contact_var.get(),
                self.teacher_name_var.get(),
                student_id
            ))
            conn.commit()

            self.load_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Student updated successfully")

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def delete_student(self):
        if not self.student_id_var.get().isdigit():
            messagebox.showerror("Error", "Enter valid Student ID")
            return

        student_id = int(self.student_id_var.get())
        if not messagebox.askyesno("Confirm", f"Delete Student ID {student_id}?"):
            return

        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM student WHERE Student_id=%s", (student_id,))
        conn.commit()

        self.load_data()
        self.clear_fields()
        cursor.close()
        conn.close()

    def clear_fields(self):
        for var in (
            self.student_name_var,
            self.student_id_var,
            self.grade_var,
            self.guardian_name_var,
            self.guardian_contact_var,
            self.teacher_name_var,
        ):
            var.set("")
        self.photo_label.config(image="")
        self.photo_path = None

    def on_table_select(self, _):
        selected = self.student_table.focus()
        if not selected:
            return

        student_id = self.student_table.item(selected, "values")[0]
        conn = db_connect()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM student WHERE Student_id=%s", (student_id,))
        student = cursor.fetchone()

        if student:
            self.student_id_var.set(student["Student_id"])
            self.student_name_var.set(student["Student_name"])
            self.grade_var.set(student["grade_lvl"])
            self.guardian_name_var.set(student["Guardian_name"])
            self.guardian_contact_var.set(student["Guardian_contact"])
            self.teacher_name_var.set(student["Teacher_name"])

            photo_path = student.get("photo_path")
            if photo_path and os.path.exists(photo_path):
                img = Image.open(photo_path).resize((160, 160))
                self.photo = ImageTk.PhotoImage(img)
                self.photo_label.config(image=self.photo)
                self.photo_label.image = self.photo
                self.photo_path = photo_path
            else:
                self.photo_label.config(image="")
                self.photo_path = None

        cursor.close()
        conn.close()
