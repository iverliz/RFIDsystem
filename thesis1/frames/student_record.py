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

        # ================= PAGINATION =================
        self.page_size = 100
        self.current_page = 1
        self.total_students = 0

        # ================= VALIDATORS =================
        self.num_validate = self.register(self.only_numbers)
        self.contact_validate = self.register(self.contact_limit)

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

        self.guardian_contact_var.trace_add("write", self.format_contact)

        # ================= FORM =================
        fields = [
            ("Full Name:", self.student_name_var),
            ("Grade:", self.grade_var),
            ("Student ID:", self.student_id_var),
            ("Guardian Name:", self.guardian_name_var),
            ("Guardian Contact:", self.guardian_contact_var),
            ("Teacher Name:", self.teacher_name_var),
        ]

        self.entries = {}
        y = 200

        for i, (label, var) in enumerate(fields):
            tk.Label(
                self.left_box,
                text=label,
                bg="white",
                font=("Arial", 11)
            ).place(x=20, y=y + i * 35)

            if label == "Grade:":
                entry = ttk.Spinbox(
                    self.left_box,
                    from_=1,
                    to=12,
                    textvariable=var,
                    width=28,
                    state="readonly"
                )

            elif label == "Student ID:":
                entry = tk.Entry(
                    self.left_box,
                    textvariable=var,
                    width=30,
                    font=("Arial", 11),
                    validate="key",
                    validatecommand=(self.num_validate, "%P")
                )
                self.student_id_entry = entry

            elif label == "Guardian Contact:":
                entry = tk.Entry(
                    self.left_box,
                    textvariable=var,
                    width=30,
                    font=("Arial", 11),
                    validate="key",
                    validatecommand=(self.contact_validate, "%P")
                )

            else:
                entry = tk.Entry(
                    self.left_box,
                    textvariable=var,
                    width=30,
                    font=("Arial", 11)
                )

            entry.place(x=150, y=y + i * 35)
            self.entries[label] = entry

        # ================= BUTTONS =================
        btn_frame = tk.Frame(self.left_box, bg="white")
        btn_frame.place(x=40, y=410)

        tk.Button(btn_frame, text="ADD", width=10, bg="#4CAF50", fg="white",
                  font=("Arial", 10, "bold"), command=self.add_student).grid(row=0, column=0, padx=5)

        tk.Button(btn_frame, text="EDIT", width=10, bg="#2196F3", fg="white",
                  font=("Arial", 10, "bold"), command=self.edit_student).grid(row=0, column=1, padx=5)

        tk.Button(btn_frame, text="DELETE", width=10, bg="#F44336", fg="white",
                  font=("Arial", 10, "bold"), command=self.delete_student).grid(row=0, column=2, padx=5)

        # ================= RIGHT PANEL =================
        self.right_panel = tk.Frame(self, width=500, height=460, bg="white", bd=2, relief="groove")
        self.right_panel.place(x=520, y=90)
        self.right_panel.pack_propagate(False)

        tk.Label(self.right_panel, text="Search Student", font=("Arial", 14, "bold"),
                 bg="white").place(x=20, y=15)

        self.search_var = tk.StringVar()
        tk.Entry(self.right_panel, textvariable=self.search_var,
                 width=25, font=("Arial", 11)).place(x=20, y=50)

        tk.Button(self.right_panel, text="Search",
                  command=self.search_student).place(x=260, y=47)

        self.count_var = tk.StringVar()
        tk.Label(self.right_panel, textvariable=self.count_var,
                 font=("Arial", 11, "bold"),
                 fg="#0047AB", bg="white").place(x=20, y=85)

        # ================= TABLE =================
        self.student_table = ttk.Treeview(
            self.right_panel,
            columns=("Student_id", "Student_name", "grade_lvl"),
            show="headings",
            height=12
        )

        for col, txt, w in [
            ("Student_id", "Student ID", 120),
            ("Student_name", "Full Name", 220),
            ("grade_lvl", "Grade", 80)
        ]:
            self.student_table.heading(col, text=txt)
            self.student_table.column(col, width=w)

        self.student_table.place(x=20, y=120, width=450)
        self.student_table.bind("<<TreeviewSelect>>", self.on_table_select)

        # ================= PAGINATION BUTTONS =================
        nav = tk.Frame(self.right_panel, bg="white")
        nav.place(x=160, y=400)

        tk.Button(nav, text="◀ Prev", command=self.prev_page).grid(row=0, column=0, padx=5)
        tk.Button(nav, text="Next ▶", command=self.next_page).grid(row=0, column=1, padx=5)

        self.load_data()

    # ================= HELPERS =================
    def only_numbers(self, v):
        return v.isdigit() or v == ""

    def contact_limit(self, v):
        return (v.isdigit() and len(v) <= 11) or v == ""

    def format_contact(self, *_):
        val = self.guardian_contact_var.get()
        # Only prepend 0 if length is 10 and first char is 9
        if val.startswith("9") and len(val) == 10:
            self.guardian_contact_var.set("0" + val)

    # ================= PAGINATION =================
    def load_data(self):
        self.student_table.delete(*self.student_table.get_children())
        offset = (self.current_page - 1) * self.page_size

        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM student")
                self.total_students = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT Student_id, Student_name, grade_lvl
                    FROM student
                    LIMIT %s OFFSET %s
                """, (self.page_size, offset))
                rows = cursor.fetchall()

        for row in rows:
            self.student_table.insert("", "end", values=row)

        total_pages = max(1, (self.total_students + self.page_size - 1) // self.page_size)
        self.count_var.set(
            f"Students: {self.total_students} | Page {self.current_page}/{total_pages}"
        )

    def next_page(self):
        if self.current_page * self.page_size < self.total_students:
            self.current_page += 1
            self.load_data()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    # ================= VALIDATION =================
    def validate(self):
        if not self.student_name_var.get().strip():
            return "Student Name is required"
        if not self.student_id_var.get().isdigit():
            return "Student ID must be numeric"
        if not self.grade_var.get().isdigit():
            return "Grade must be numeric"
        if not self.guardian_name_var.get().strip():
            return "Guardian Name is required"
        if not self.guardian_contact_var.get().isdigit():
            return "Guardian Contact must be numeric"
        if not self.teacher_name_var.get().strip():
            return "Teacher Name is required"
        return None

    def student_id_exists(self, student_id):
        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT Student_id FROM student WHERE Student_id=%s", (student_id,))
                exists = cursor.fetchone() is not None
        return exists

    # ================= CRUD FUNCTIONS =================
    def upload_photo(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
        )
        if not path:
            return
        try:
            img = Image.open(path)
            img.thumbnail((160, 160))
            self.photo = ImageTk.PhotoImage(img)
            self.photo_label.config(image=self.photo)
            self.photo_label.image = self.photo
            self.photo_path = path
        except Exception:
            messagebox.showerror("Error", "Invalid image file")

    def add_student(self):
        error = self.validate()
        if error:
            messagebox.showerror("Error", error)
            return

        if not self.photo_path:
            messagebox.showerror("Error", "Photo is required")
            return

        student_id = int(self.student_id_var.get())
        grade = int(self.grade_var.get())

        if self.student_id_exists(student_id):
            messagebox.showerror("Error", "Student ID already exists")
            return

        img_save = os.path.join(PHOTO_DIR, f"student_{student_id}_{int(time.time())}.jpg")
        Image.open(self.photo_path).save(img_save)

        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO student
                    (Student_name, Student_id, grade_lvl, Guardian_name,
                     Guardian_contact, Teacher_name, photo_path)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                """, (
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

    def edit_student(self):
        error = self.validate()
        if error:
            messagebox.showerror("Error", error)
            return

        student_id = int(self.student_id_var.get())
        grade = int(self.grade_var.get())

        # Update photo if a new one was uploaded
        if self.photo_path:
            img_save = os.path.join(PHOTO_DIR, f"student_{student_id}_{int(time.time())}.jpg")
            Image.open(self.photo_path).save(img_save)
            photo_sql = ", photo_path=%s"
            params = (
                self.student_name_var.get(),
                grade,
                self.guardian_name_var.get(),
                self.guardian_contact_var.get(),
                self.teacher_name_var.get(),
                img_save,
                student_id
            )
        else:
            photo_sql = ""
            params = (
                self.student_name_var.get(),
                grade,
                self.guardian_name_var.get(),
                self.guardian_contact_var.get(),
                self.teacher_name_var.get(),
                student_id
            )

        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE student SET
                        Student_name=%s,
                        grade_lvl=%s,
                        Guardian_name=%s,
                        Guardian_contact=%s,
                        Teacher_name=%s
                        {photo_sql}
                    WHERE Student_id=%s
                """, params)
                conn.commit()

        self.load_data()
        self.clear_fields()
        messagebox.showinfo("Success", "Student updated successfully")

    def delete_student(self):
        if not self.student_id_var.get().isdigit():
            messagebox.showerror("Error", "Invalid Student ID")
            return

        student_id = int(self.student_id_var.get())
        if not messagebox.askyesno("Confirm", f"Delete Student ID {student_id}?"):
            return

        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT photo_path FROM student WHERE Student_id=%s", (student_id,))
                row = cursor.fetchone()
                if row and row[0] and os.path.exists(row[0]):
                    os.remove(row[0])

                cursor.execute("DELETE FROM student WHERE Student_id=%s", (student_id,))
                conn.commit()

        self.load_data()
        self.clear_fields()

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
        self.photo_label.image = None
        self.photo_path = None
        self.student_id_entry.config(state="normal")

    def search_student(self):
        keyword = self.search_var.get()
        with db_connect() as conn:
            with conn.cursor() as cursor:
              cursor.execute("""
                SELECT Student_id, Student_name, grade_lvl
                FROM student
                WHERE Student_name LIKE %s OR Student_id LIKE %s
            """, (f"%{keyword}%", f"%{keyword}%"))
            self.search_results = cursor.fetchall()

        self.search_page = 1
        self.update_search_table()


    def on_table_select(self, _):
        selected = self.student_table.focus()
        if not selected:
            return

        self.student_id_entry.config(state="disabled")
        student_id = self.student_table.item(selected, "values")[0]

        with db_connect() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM student WHERE Student_id=%s", (student_id,))
                student = cursor.fetchone()

        if student:
            self.student_id_var.set(student["Student_id"])
            self.student_name_var.set(student["Student_name"])
            self.grade_var.set(student["grade_lvl"])
            self.guardian_name_var.set(student["Guardian_name"])
            self.guardian_contact_var.set(student["Guardian_contact"])
            self.teacher_name_var.set(student["Teacher_name"])

            if student["photo_path"] and os.path.exists(student["photo_path"]):
                img = Image.open(student["photo_path"])
                img.thumbnail((160, 160))
                self.photo = ImageTk.PhotoImage(img)
                self.photo_label.config(image=self.photo)
                self.photo_label.image = self.photo
                self.photo_path = student["photo_path"]

    def update_search_table(self):
        self.student_table.delete(*self.student_table.get_children())
        start = (self.search_page - 1) * self.search_page_size
        end = start + self.search_page_size
        page_rows = self.search_results[start:end]

        for row in page_rows:
            self.student_table.insert("", "end", values=row)

        total_pages = max(1, (len(self.search_results) + self.search_page_size - 1) // self.search_page_size)
        self.count_var.set(f"Search Results: {len(self.search_results)} | Page {self.search_page}/{total_pages}")

    def next_search_page(self):
        total_pages = max(1, (len(self.search_results) + self.search_page_size - 1) // self.search_page_size)
        if self.search_page < total_pages:
            self.search_page += 1
        self.update_search_table()

    def prev_search_page(self):
        if self.search_page > 1:
            self.search_page -= 1
        self.update_search_table()

