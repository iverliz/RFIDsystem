import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import ImageTk, Image
import os
import sys

# ================= PATH SETUP =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.database import db_connect

PHOTO_DIR = os.path.join(BASE_DIR, "teacher_photos")
os.makedirs(PHOTO_DIR, exist_ok=True)


class TeacherRecord(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#b2e5ed")
        self.controller = controller
        self.photo_path = None
        self.photo = None

        # ================= HEADER =================
        header = tk.Frame(self, height=70, bg="#0047AB")
        header.pack(fill="x")

        tk.Label(
            header, text="TEACHER INFORMATION",
            font=("Arial", 20, "bold"),
            bg="#0047AB", fg="white"
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
            self.left_box, text="Upload Photo",
            width=14, command=self.upload_photo
        ).place(x=210, y=80)

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

        tk.Button(self.right_panel, text="Search",
                  command=self.search_teacher).place(x=260, y=47)

        self.teacher_count_var = tk.StringVar(value="Total Teachers: 0")
        tk.Label(self.right_panel, textvariable=self.teacher_count_var,
                 font=("Arial", 11, "bold"),
                 fg="#0047AB", bg="white").place(x=20, y=85)

        # ================= TABLE =================
        columns = ("name", "grade", "photo")
        self.teacher_table = ttk.Treeview(self.right_panel, columns=columns, show="headings", height=12)

        self.teacher_table.heading("name", text="Teacher Name")
        self.teacher_table.heading("grade", text="Grade")
        self.teacher_table.heading("photo", text="Photo")

        self.teacher_table.column("name", width=260)
        self.teacher_table.column("grade", width=160)
        self.teacher_table.column("photo", width=0, stretch=False)  # hide photo path

        self.teacher_table.place(x=20, y=120, width=450)
        self.teacher_table.bind("<<TreeviewSelect>>", self.on_select)

        self.load_teachers()

    # ================= FUNCTIONS =================
    def upload_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if path:
            img = Image.open(path).resize((160, 160))
            self.photo = ImageTk.PhotoImage(img)
            self.photo_label.config(image=self.photo)
            self.photo_label.image = self.photo
            self.photo_path = path

    def load_teachers(self):
        self.teacher_table.delete(*self.teacher_table.get_children())
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT teacher_name, teacher_grade, photo_path FROM teacher")
        rows = cursor.fetchall()

        for row in rows:
            self.teacher_table.insert("", "end", values=row)

        self.teacher_count_var.set(f"Total Teachers: {len(rows)}")
        cursor.close()
        conn.close()

    def add_teacher(self):
        if not self.teacher_name_var.get() or not self.teacher_grade_var.get():
            messagebox.showerror("Error", "All fields are required")
            return

        photo_save = None
        if self.photo_path:
            filename = self.teacher_name_var.get().replace(" ", "_") + ".jpg"
            photo_save = os.path.join(PHOTO_DIR, filename)

            img = Image.open(self.photo_path).convert("RGB")
            img.save(photo_save, "JPEG")

        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO teacher (teacher_name, teacher_grade, photo_path) VALUES (%s, %s, %s)",
            (self.teacher_name_var.get(), self.teacher_grade_var.get(), photo_save)
        )
        conn.commit()
        cursor.close()
        conn.close()

        self.load_teachers()
        self.clear_fields()
        messagebox.showinfo("Success", "Teacher added")

    def edit_teacher(self):
        selected = self.teacher_table.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a teacher first")
            return

        old_name, _, old_photo = self.teacher_table.item(selected, "values")
        photo_save = old_photo

        if self.photo_path:
            filename = self.teacher_name_var.get().replace(" ", "_") + ".jpg"
            photo_save = os.path.join(PHOTO_DIR, filename)
            img = Image.open(self.photo_path).convert("RGB")
            img.save(photo_save, "JPEG")

        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE teacher SET teacher_name=%s, teacher_grade=%s, photo_path=%s WHERE teacher_name=%s",
            (self.teacher_name_var.get(), self.teacher_grade_var.get(), photo_save, old_name)
        )
        conn.commit()
        cursor.close()
        conn.close()

        self.load_teachers()
        self.clear_fields()
        messagebox.showinfo("Updated", "Teacher updated")

    def delete_teacher(self):
        selected = self.teacher_table.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a teacher first")
            return

        name, _, photo_path = self.teacher_table.item(selected, "values")

        if not messagebox.askyesno("Confirm", "Delete this teacher?"):
            return

        if photo_path and os.path.exists(photo_path):
            os.remove(photo_path)

        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM teacher WHERE teacher_name=%s", (name,))
        conn.commit()
        cursor.close()
        conn.close()

        self.load_teachers()
        self.clear_fields()

    def search_teacher(self):
        keyword = self.search_var.get()
        self.teacher_table.delete(*self.teacher_table.get_children())

        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT teacher_name, teacher_grade, photo_path FROM teacher WHERE teacher_name LIKE %s or teacher_grade",
            (f"%{keyword}%",)
        )
        rows = cursor.fetchall()

        for row in rows:
            self.teacher_table.insert("", "end", values=row)

        self.teacher_count_var.set(f"Total Teachers: {len(rows)}")
        cursor.close()
        conn.close()

    def on_select(self, _):
        selected = self.teacher_table.focus()
        if not selected:
            return

        name, grade, photo_path = self.teacher_table.item(selected, "values")
        self.teacher_name_var.set(name)
        self.teacher_grade_var.set(grade)

        if photo_path and os.path.exists(photo_path):
            img = Image.open(photo_path).resize((160, 160))
            self.photo = ImageTk.PhotoImage(img)
            self.photo_label.config(image=self.photo)
            self.photo_label.image = self.photo
        else:
            self.photo_label.config(image="")
            self.photo_label.image = None

        self.photo_path = None

    def clear_fields(self):
        self.teacher_name_var.set("")
        self.teacher_grade_var.set("")
        self.photo_label.config(image="")
        self.photo_label.image = None
        self.photo_path = None
