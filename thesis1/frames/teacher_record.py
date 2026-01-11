import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import ImageTk, Image
import os
import time
from utils.database import db_connect
import sys

PHOTO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "teacher_photos")
os.makedirs(PHOTO_DIR, exist_ok=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

class TeacherRecord(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#b2e5ed")
        self.controller = controller

        self.photo_path = None  # current photo path (from DB or uploaded)
        self.photo = None

        # ================= PAGINATION =================
        self.page_size = 50
        self.current_page = 1
        self.total_teachers = 0
        self.search_results = None
        self.search_page = 1

        # ================= HEADER =================
        header = tk.Frame(self, height=70, bg="#0047AB")
        header.pack(fill="x")
        tk.Label(header, text="TEACHER INFORMATION",
                 font=("Arial", 20, "bold"), bg="#0047AB", fg="white").place(x=30, y=18)

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

        tk.Button(self.left_box, text="Upload Photo", width=14, command=self.upload_photo).place(x=210, y=80)

        # ================= VARIABLES =================
        self.teacher_name_var = tk.StringVar()
        self.teacher_grade_var = tk.StringVar()

        # ================= FORM =================
        tk.Label(self.left_box, text="Teacher Name:", bg="white", font=("Arial", 11)).place(x=20, y=200)
        tk.Entry(self.left_box, textvariable=self.teacher_name_var, width=30, font=("Arial", 11)).place(x=150, y=200)

        tk.Label(self.left_box, text="Grade:", bg="white", font=("Arial", 11)).place(x=20, y=240)
        tk.Entry(self.left_box, textvariable=self.teacher_grade_var, width=30, font=("Arial", 11)).place(x=150, y=240)

        # ================= BUTTONS =================
        btn_frame = tk.Frame(self.left_box, bg="white")
        btn_frame.place(x=40, y=320)

        tk.Button(btn_frame, text="ADD", width=10, bg="#4CAF50",
                  fg="white", font=("Arial", 10, "bold"),
                  command=self.add_teacher).grid(row=0, column=0, padx=5)

        tk.Button(btn_frame, text="EDIT", width=10, bg="#2196F3",
                  fg="white", font=("Arial", 10, "bold"),
                  command=self.edit_teacher).grid(row=0, column=1, padx=5)

        tk.Button(btn_frame, text="DELETE", width=10, bg="#F44336",
                  fg="white", font=("Arial", 10, "bold"),
                  command=self.delete_teacher).grid(row=0, column=2, padx=5)

        # ================= RIGHT PANEL =================
        self.right_panel = tk.Frame(self, width=500, height=460, bg="white", bd=2, relief="groove")
        self.right_panel.place(x=520, y=90)
        self.right_panel.pack_propagate(False)

        tk.Label(self.right_panel, text="Search Teacher",
                 font=("Arial", 14, "bold"), bg="white").place(x=20, y=15)

        self.search_var = tk.StringVar()
        tk.Entry(self.right_panel, textvariable=self.search_var,
                 width=25, font=("Arial", 11)).place(x=20, y=50)

        tk.Button(self.right_panel, text="Search", command=self.search_teacher).place(x=260, y=47)

        self.teacher_count_var = tk.StringVar(value="Total Teachers: 0 | Page 1/1")
        tk.Label(self.right_panel, textvariable=self.teacher_count_var,
                 font=("Arial", 11, "bold"), fg="#0047AB", bg="white").place(x=20, y=85)

        # ================= TABLE =================
        columns = ("teacher_id", "name", "grade")  # hidden id column for internal use
        self.teacher_table = ttk.Treeview(self.right_panel, columns=columns, show="headings", height=12)
        self.teacher_table.heading("teacher_id", text="teacher_id")
        self.teacher_table.heading("name", text="Teacher Name")
        self.teacher_table.heading("grade", text="Grade")

        self.teacher_table.column("teacher_id", width=0, stretch=False)  # hide ID
        self.teacher_table.column("name", width=260)
        self.teacher_table.column("grade", width=160)

        self.teacher_table.place(x=20, y=120, width=450)
        self.teacher_table.bind("<<TreeviewSelect>>", self.on_select)

        # ================= PAGINATION BUTTONS =================
        nav = tk.Frame(self.right_panel, bg="white")
        nav.place(x=160, y=400)
        tk.Button(nav, text="◀ Prev", command=self.prev_page).grid(row=0, column=0, padx=5)
        tk.Button(nav, text="Next ▶", command=self.next_page).grid(row=0, column=1, padx=5)

        # ================= LOAD DATA =================
        self.load_teachers()

    # ================= PHOTO HELPERS =================
    def upload_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if path:
            self.photo_path = path
            self.photo = self.load_image(path)
            self.photo_label.config(image=self.photo)
            self.photo_label.image = self.photo

    def load_image(self, path, size=(160, 160)):
        img = Image.open(path).resize(size)
        return ImageTk.PhotoImage(img)

    # ================= VALIDATION =================
    def validate_fields(self):
        if not self.teacher_name_var.get().strip():
            return "Teacher Name is required"
        if not self.teacher_grade_var.get().isdigit():
            return "Grade must be numeric"
        return None

    # ================= CRUD =================
    def add_teacher(self):
        error = self.validate_fields()
        if error:
            messagebox.showerror("Error", error)
            return

        photo_save = None
        if self.photo_path:
            filename = f"{self.teacher_name_var.get().replace(' ', '_')}_{int(time.time())}.jpg"
            photo_save = os.path.join(PHOTO_DIR, filename)
            Image.open(self.photo_path).convert("RGB").save(photo_save, "JPEG")

        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO teacher (teacher_name, teacher_grade, photo_path) VALUES (%s, %s, %s)",
                    (self.teacher_name_var.get().strip(), int(self.teacher_grade_var.get()), photo_save)
                )
                conn.commit()

        self.clear_fields()
        self.load_teachers()
        messagebox.showinfo("Success", "Teacher added")

    def edit_teacher(self):
        selected = self.teacher_table.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a teacher first")
            return

        teacher_id, _, _ = self.teacher_table.item(selected, "values")

        with db_connect() as conn:
            with conn.cursor() as cursor:
                # Handle photo update
                cursor.execute("SELECT photo_path FROM teacher WHERE teacher_id=%s", (teacher_id,))
                old_photo_path = cursor.fetchone()[0]
                photo_save = old_photo_path

                if self.photo_path:
                    if old_photo_path and os.path.exists(old_photo_path):
                        os.remove(old_photo_path)
                    filename = f"{self.teacher_name_var.get().replace(' ', '_')}_{int(time.time())}.jpg"
                    photo_save = os.path.join(PHOTO_DIR, filename)
                    Image.open(self.photo_path).convert("RGB").save(photo_save, "JPEG")

                # Update DB
                cursor.execute(
                    "UPDATE teacher SET teacher_name=%s, teacher_grade=%s, photo_path=%s WHERE teacher_id=%s",
                    (self.teacher_name_var.get().strip(), int(self.teacher_grade_var.get()), photo_save, teacher_id)
                )
                conn.commit()

        self.clear_fields()
        self.load_teachers()
        messagebox.showinfo("Updated", "Teacher updated")

    def delete_teacher(self):
        selected = self.teacher_table.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a teacher first")
            return

        teacher_id, _, _ = self.teacher_table.item(selected, "values")
        if not messagebox.askyesno("Confirm", "Delete this teacher?"):
            return

        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT photo_path FROM teacher WHERE teacher_id=%s", (teacher_id,))
                photo_path = cursor.fetchone()[0]
                if photo_path and os.path.exists(photo_path):
                    os.remove(photo_path)
                cursor.execute("DELETE FROM teacher WHERE teacher_id=%s", (teacher_id,))
                conn.commit()

        self.clear_fields()
        self.load_teachers()

    # ================= LOAD TEACHERS =================
    def load_teachers(self, search=False):
        self.teacher_table.delete(*self.teacher_table.get_children())

        if search and self.search_results is not None:
            data = self.search_results
            total = len(data)
        else:
            offset = (self.current_page - 1) * self.page_size
            with db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM teacher")
                    self.total_teachers = cursor.fetchone()[0]

                    cursor.execute(
                        "SELECT teacher_id, teacher_name, teacher_grade FROM teacher "
                        "ORDER BY teacher_name LIMIT %s OFFSET %s",
                        (self.page_size, offset)
                    )
                    data = cursor.fetchall()
                    total = self.total_teachers

        for row in data:
            self.teacher_table.insert("", "end", values=row)

        total_pages = max(1, (total + self.page_size - 1) // self.page_size)
        page = self.current_page if not search else self.search_page
        self.teacher_count_var.set(f"Total Teachers: {total} | Page {page}/{total_pages}")

    def next_page(self):
        if self.search_results:  # paginate search results
            total_pages = max(1, (len(self.search_results) + self.page_size - 1) // self.page_size)
            if self.search_page < total_pages:
                self.search_page += 1
                self.load_teachers(search=True)
        else:
            if self.current_page * self.page_size < self.total_teachers:
                self.current_page += 1
                self.load_teachers()

    def prev_page(self):
        if self.search_results:
            if self.search_page > 1:
                self.search_page -= 1
                self.load_teachers(search=True)
        else:
            if self.current_page > 1:
                self.current_page -= 1
                self.load_teachers()

    # ================= SEARCH =================
    def search_teacher(self):
        keyword = self.search_var.get().strip()
        if not keyword:
            self.search_results = None
            self.current_page = 1
            self.load_teachers()
            return

        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT teacher_id, teacher_name, teacher_grade FROM teacher "
                    "WHERE teacher_name LIKE %s OR teacher_grade LIKE %s",
                    (f"%{keyword}%", f"%{keyword}%")
                )
                self.search_results = cursor.fetchall()
                self.search_page = 1
                self.load_teachers(search=True)

    # ================= TABLE SELECT =================
    def on_select(self, _):
        selected = self.teacher_table.focus()
        if not selected:
            return

        teacher_id, name, grade = self.teacher_table.item(selected, "values")
        self.teacher_name_var.set(name)
        self.teacher_grade_var.set(grade)

        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT photo_path FROM teacher WHERE teacher_id=%s", (teacher_id,))
                photo_path = cursor.fetchone()[0]
                if photo_path and os.path.exists(photo_path):
                    self.photo = self.load_image(photo_path)
                    self.photo_label.config(image=self.photo)
                    self.photo_label.image = self.photo
                    self.photo_path = photo_path
                else:
                    self.photo_label.config(image="")
                    self.photo_label.image = None
                    self.photo_path = None

    # ================= CLEAR =================
    def clear_fields(self):
        self.teacher_name_var.set("")
        self.teacher_grade_var.set("")
        self.photo_label.config(image="")
        self.photo_label.image = None
        self.photo_path = None
        self.search_results = None
