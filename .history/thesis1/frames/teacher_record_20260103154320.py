import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import ImageTk, Image
import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.database import db_connect

PHOTO_DIR = os.path.join(BASE_DIR, "teacher_photos")
os.makedirs(PHOTO_DIR, exist_ok=True)


class TeacherInfo(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg="#b2e5ed")
        self.root = root
        self.photo_path = None

        root.title("TEACHER MANAGEMENT SYSTEM - TEACHER RECORD")
        root.geometry("1350x700+0+0")
        self.pack(fill="both", expand=True)

        # HEADER
        header = tk.Frame(self, height=95, bg="#0047AB", bd=2, relief="groove")
        header.pack(fill="x")
        tk.Label(header, text="TEACHER INFORMATION",
                 font=("Arial", 24, "bold"),
                 bg="#0047AB", fg="white").place(x=50, y=25)

        # LEFT BOX
        self.left_box = tk.Frame(self, width=500, height=550, bg="white", bd=2, relief="groove")
        self.left_box.place(x=50, y=125)
        self.left_box.pack_propagate(False)

        # PHOTO
        self.photo_frame = tk.Frame(self.left_box, width=200, height=200, bg="#E0E0E0", bd=2, relief="ridge")
        self.photo_frame.place(x=20, y=20)
        self.photo_frame.pack_propagate(False)

        self.photo_label = tk.Label(self.photo_frame, bg="#E0E0E0")
        self.photo_label.pack(fill="both", expand=True)

        tk.Button(self.left_box, text="Upload Photo", width=15,
                  command=self.upload_photo).place(x=60, y=240)

        # VARIABLES
        self.teacher_name_var = tk.StringVar()
        self.teacher_grade_var = tk.StringVar()

        y = 290
        fields = [
            ("Teacher Name:", self.teacher_name_var),
            ("Grade:", self.teacher_grade_var)
        ]

        for i, (label, var) in enumerate(fields):
            tk.Label(self.left_box, text=label, bg="white",
                     font=("Arial", 12)).place(x=20, y=y + i * 40)
            tk.Entry(self.left_box, textvariable=var,
                     font=("Arial", 12), width=30).place(x=160, y=y + i * 40)

        # BUTTONS
        tk.Button(self.left_box, text="ADD", width=10,
                  bg="#4CAF50", fg="white",
                  command=self.add_teacher).place(x=40, y=510)

        tk.Button(self.left_box, text="EDIT", width=10,
                  bg="#2196F3", fg="white",
                  command=self.edit_teacher).place(x=180, y=510)

        tk.Button(self.left_box, text="DELETE", width=10,
                  bg="#F44336", fg="white",
                  command=self.delete_teacher).place(x=320, y=510)

        # RIGHT PANEL
        self.right_panel = tk.Frame(self, width=550, height=500, bg="white", bd=2, relief="groove")
        self.right_panel.place(x=700, y=150)
        self.right_panel.pack_propagate(False)

        tk.Label(self.right_panel, text="Search Teacher",
                 font=("Arial", 16, "bold"),
                 bg="white").place(x=20, y=20)

        self.search_var = tk.StringVar()
        tk.Entry(self.right_panel, textvariable=self.search_var,
                 font=("Arial", 12), width=25).place(x=20, y=60)

        tk.Button(self.right_panel, text="Search",
                  command=self.search_teacher).place(x=300, y=57)

        self.teacher_count_var = tk.StringVar(value="Total Teachers: 0")
        tk.Label(self.right_panel, textvariable=self.teacher_count_var,
                 font=("Arial", 12, "bold"),
                 fg="#0047AB", bg="white").place(x=20, y=100)

        columns = ("name", "grade")
        self.teacher_table = ttk.Treeview(self.right_panel,
                                          columns=columns,
                                          show="headings",
                                          height=12)

        self.teacher_table.heading("name", text="Teacher Name")
        self.teacher_table.heading("grade", text="Grade")
        self.teacher_table.place(x=20, y=140, width=500)
        self.teacher_table.bind("<<TreeviewSelect>>", self.on_select)

        self.load_teachers()

    # ---------------- FUNCTIONS ----------------

    def upload_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
        if path:
            img = Image.open(path).resize((200, 200))
            self.photo = ImageTk.PhotoImage(img)
            self.photo_label.config(image=self.photo)
            self.photo_label.image = self.photo
            self.photo_path = path

    def load_teachers(self):
        self.teacher_table.delete(*self.teacher_table.get_children())
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT teacher_name, teacher_grade FROM teacher")
        rows = cursor.fetchall()

        for row in rows:
            self.teacher_table.insert("", "end", values=row)

        self.teacher_count_var.set(f"Total Teachers: {len(rows)}")
        cursor.close()
        conn.close()

    def add_teacher(self):
        if not self.teacher_name_var.get() or not self.teacher_grade_var.get():
            messagebox.showerror("Error", "All fields required")
            return

        photo_save = None
        if self.photo_path:
            photo_save = os.path.join(PHOTO_DIR, f"{self.teacher_name_var.get().replace(' ', '_')}.jpg")
            Image.open(self.photo_path).save(photo_save)

        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO teacher (teacher_name, teacher_grade, photo_path) VALUES (%s,%s,%s)",
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
            return

        old_name = self.teacher_table.item(selected, "values")[0]

        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE teacher SET teacher_name=%s, teacher_grade=%s WHERE teacher_name=%s",
            (self.teacher_name_var.get(), self.teacher_grade_var.get(), old_name)
        )
        conn.commit()
        cursor.close()
        conn.close()

        self.load_teachers()
        messagebox.showinfo("Updated", "Teacher updated")

    def delete_teacher(self):
        selected = self.teacher_table.focus()
        if not selected:
            return

        name = self.teacher_table.item(selected, "values")[0]

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
            "SELECT teacher_name, teacher_grade FROM teacher WHERE teacher_name LIKE %s",
            (f"%{keyword}%",)
        )

        rows = cursor.fetchall()
        for row in rows:
            self.teacher_table.insert("", "end", values=row)

        self.teacher_count_var.set(f"Total Teachers: {len(rows)}")
        cursor.close()
        conn.close()

    def on_select(self, event):
        selected = self.teacher_table.focus()
        if not selected:
            return

        name, grade = self.teacher_table.item(selected, "values")
        self.teacher_name_var.set(name)
        self.teacher_grade_var.set(grade)

    def clear_fields(self):
        self.teacher_name_var.set("")
        self.teacher_grade_var.set("")
        self.photo_label.config(image="")
        self.photo_path = None


