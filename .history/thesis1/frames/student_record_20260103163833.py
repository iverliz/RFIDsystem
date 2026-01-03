import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import ImageTk, Image
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from utils.database import db_connect

PHOTO_DIR = os.path.join(BASE_DIR, "student_photos")
os.makedirs(PHOTO_DIR, exist_ok=True)

class StudentRecord(tk.Frame):
    def __init__(self, parent):
        super().__init__(root, bg="#b2e5ed")
        self.root = root
        self.photo_path = None

        root.title("RFID MANAGEMENT SYSTEM - STUDENT RECORD")
        root.geometry("1350x700+0+0")
        self.pack(fill="both", expand=True)

        # HEADER
        header = tk.Frame(self, height=95, bg="#0047AB")
        header.pack(fill="x")
        tk.Label(header, text="STUDENT INFORMATION",
                 font=("Arial", 24, "bold"), bg="#0047AB", fg="white").place(x=50, y=25)

        # LEFT PANEL
        self.student_left = tk.Frame(self, width=500, height=550, bg="white")
        self.student_left.place(x=50, y=125)
        self.student_left.pack_propagate(False)

        # PHOTO
        self.photo_frame = tk.Frame(self.student_left, width=200, height=200, bg="#E0E0E0")
        self.photo_frame.place(x=20, y=20)
        self.photo_label = tk.Label(self.photo_frame)
        self.photo_label.pack(fill="both", expand=True)
        tk.Button(self.student_left, text="Upload Photo", command=self.upload_photo).place(x=60, y=240)

        # VARIABLES
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
            tk.Label(self.student_left, text=label, bg="white").place(x=20, y=y + i * 40)
            tk.Entry(self.student_left, textvariable=var, width=30).place(x=160, y=y + i * 40)

        # BUTTONS
        tk.Button(self.student_left, text="ADD", command=self.add_student, bg="#4CAF50", fg="white").place(x=40, y=510)
        tk.Button(self.student_left, text="EDIT", command=self.edit_student, bg="#2196F3", fg="white").place(x=180, y=510)
        tk.Button(self.student_left, text="DELETE", command=self.delete_student, bg="#F44336", fg="white").place(x=320, y=510)

        # RIGHT PANEL
        self.right_panel = tk.Frame(self, width=550, height=500, bg="white")
        self.right_panel.place(x=700, y=150)

        self.student_table = ttk.Treeview(
            self.right_panel,
            columns=("Student_id", "Student_name", "grade_lvl"),
            show="headings", height=12
        )
        self.student_table.heading("Student_id", text="Student ID")
        self.student_table.heading("Student_name", text="Full Name")
        self.student_table.heading("grade_lvl", text="Grade")
        self.student_table.place(x=20, y=20, width=500)

        # BIND CLICK ON TABLE
        self.student_table.bind("<<TreeviewSelect>>", self.on_table_select)

        self.load_data()

    # FUNCTIONS
    def upload_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if path:
            img = Image.open(path).resize((200, 200))
            self.photo = ImageTk.PhotoImage(img)
            self.photo_label.config(image=self.photo)
            self.photo_label.image = self.photo
            self.photo_path = path

    def student_id_exists(self, student_id):
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT Student_id FROM student WHERE Student_id=%s", (student_id,))
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
            for row in cursor.fetchall():
                self.student_table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def add_student(self):
        try:
            if not self.photo_path:
                messagebox.showerror("Error", "Photo is required")
                return
            student_id = int(self.student_id_var.get())
            grade = int(self.grade_var.get())
            if self.student_id_exists(student_id):
                messagebox.showerror("Error", "Student ID already exists")
                return
            img_save = os.path.join(PHOTO_DIR, f"student_{student_id}.jpg")
            Image.open(self.photo_path).save(img_save)

            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO student
                (Student_name, Student_id, grade_lvl, Guardian_name, Guardian_contact, Teacher_name, photo_path)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (self.student_name_var.get(), student_id, grade,
                  self.guardian_name_var.get(), self.guardian_contact_var.get(),
                  self.teacher_name_var.get(), img_save))
            conn.commit()
            self.load_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Student added successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def edit_student(self):
        try:
            student_id = int(self.student_id_var.get())
            grade = int(self.grade_var.get())
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE student SET
                    Student_name=%s,
                    grade_lvl=%s,
                    Guardian_name=%s,
                    Guardian_contact=%s,
                    Teacher_name=%s
                WHERE Student_id=%s
            """, (self.student_name_var.get(), grade,
                  self.guardian_name_var.get(), self.guardian_contact_var.get(),
                  self.teacher_name_var.get(), student_id))
            conn.commit()
            self.load_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Student updated successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def delete_student(self):
        if not self.student_id_var.get().isdigit():
            messagebox.showerror("Error", "Please enter a valid Student ID")
            return

        student_id = int(self.student_id_var.get())
        confirm = messagebox.askyesno("Confirm Delete", f"Delete Student ID {student_id}?")
        if not confirm:
            return

        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM student WHERE Student_id=%s", (student_id,))
            if cursor.rowcount == 0:
                messagebox.showerror("Error", "Student not found")
                return
            conn.commit()
            self.load_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Student deleted successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def clear_fields(self):
        for v in [self.student_name_var, self.student_id_var, self.grade_var,
                  self.guardian_name_var, self.guardian_contact_var, self.teacher_name_var]:
            v.set("")
        self.photo_label.config(image="")
        self.photo_path = None

    def on_table_select(self, event):
        selected = self.student_table.focus()
        if not selected:
            return
        values = self.student_table.item(selected, "values")
        student_id = values[0]

        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM student WHERE Student_id=%s", (student_id,))
            student = cursor.fetchone()
            if not student:
                return
            self.student_id_var.set(student["Student_id"])
            self.student_name_var.set(student["Student_name"])
            self.grade_var.set(student["grade_lvl"])
            self.guardian_name_var.set(student["Guardian_name"])
            self.guardian_contact_var.set(student["Guardian_contact"])
            self.teacher_name_var.set(student["Teacher_name"])

            photo_path = student.get("photo_path")
            if photo_path and os.path.exists(photo_path):
                img = Image.open(photo_path).resize((200, 200))
                self.photo = ImageTk.PhotoImage(img)
                self.photo_label.config(image=self.photo)
                self.photo_label.image = self.photo
                self.photo_path = photo_path
            else:
                self.photo_label.config(image="")
                self.photo_path = None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()


