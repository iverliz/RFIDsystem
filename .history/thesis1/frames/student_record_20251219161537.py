import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import ImageTk, Image
import mysql.connector
import io


class Student(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg="#b2e5ed")
        self.root = root

        root.title("RFID MANAGEMENT SYSTEM - STUDENT RECORD")
        root.geometry("1350x700+0+0")

        self.pack(fill="both", expand=True)

        self.connect_db()
        self.photo_data = None

        # ================= HEADER =================
        self.student_frame = tk.Frame(self, height=95, bg="#0047AB", bd=2, relief="groove")
        self.student_frame.pack(fill="x")

        tk.Label(self.student_frame, text="STUDENT INFORMATION",
                 font=("Arial", 24, "bold"), bg="#0047AB", fg="white").place(x=50, y=25)

        # ================= LEFT BOX =================
        self.student_left = tk.Frame(self, width=500, height=550, bg="white", bd=2, relief="groove")
        self.student_left.place(x=50, y=125)
        self.student_left.pack_propagate(False)

        self.photo_frame = tk.Frame(self.student_left, width=200, height=200,
                                    bg="#E0E0E0", bd=2, relief="ridge")
        self.photo_frame.place(x=20, y=20)
        self.photo_frame.pack_propagate(False)

        self.photo_label = tk.Label(self.photo_frame, bg="#E0E0E0")
        self.photo_label.pack(fill="both", expand=True)

        tk.Button(self.student_left, text="Upload Photo",
                  command=self.upload_photo).place(x=60, y=240)

        # ================= STUDENT DETAILS =================
        y = 290
        label_font = ("Arial", 12)
        entry_font = ("Arial", 12)

        self.fullname_var = tk.StringVar()
        self.grade_var = tk.StringVar()
        self.student_id_var = tk.StringVar()
        self.guardian_name_var = tk.StringVar()
        self.guardian_contact_var = tk.StringVar()
        self.rfid_uid_var = tk.StringVar()

        fields = [
            ("Full Name:", self.fullname_var),
            ("Grade Level:", self.grade_var),
            ("Student ID:", self.student_id_var),
            ("Guardian Name:", self.guardian_name_var),
            ("Guardian Contact:", self.guardian_contact_var),
            ("RFID UID:", self.rfid_uid_var),
        ]

        for i, (label, var) in enumerate(fields):
            tk.Label(self.student_left, text=label, bg="white",
                     font=label_font).place(x=20, y=y + i * 40)
            tk.Entry(self.student_left, textvariable=var,
                     font=entry_font, width=30).place(x=160, y=y + i * 40)

        tk.Button(self.student_left, text="ADD", bg="#4CAF50", fg="white",
                  command=self.add_student).place(x=40, y=510)
        tk.Button(self.student_left, text="EDIT", bg="#2196F3", fg="white",
                  command=self.edit_student).place(x=180, y=510)
        tk.Button(self.student_left, text="DELETE", bg="#F44336", fg="white",
                  command=self.delete_student).place(x=320, y=510)

        # ================= RIGHT PANEL =================
        self.right_panel = tk.Frame(self, width=550, height=500, bg="white", bd=2, relief="groove")
        self.right_panel.place(x=700, y=150)
        self.right_panel.pack_propagate(False)

        columns = ("id", "name", "grade")
        self.student_table = ttk.Treeview(self.right_panel, columns=columns,
                                          show="headings", height=14)
        for col, txt in zip(columns, ["Student ID", "Full Name", "Grade"]):
            self.student_table.heading(col, text=txt)
            self.student_table.column(col, width=160)

        self.student_table.place(x=20, y=20, width=500)
        self.student_table.bind("<<TreeviewSelect>>", self.load_selected_student)

        self.rfid_buffer = ""
        self.root.bind("<Key>", self.capture_rfid)

        self.fetch_students()

    # ================= DATABASE =================
    def connect_db(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="rfid_system"
        )
        self.cursor = self.db.cursor()

    # ================= RFID =================
    def capture_rfid(self, event):
        if event.keysym == "Return":
            self.rfid_uid_var.set(self.rfid_buffer)
            self.student_id_var.set(self.rfid_buffer)
            self.rfid_buffer = ""
        elif event.char.isalnum():
            self.rfid_buffer += event.char

    # ================= PHOTO =================
    def upload_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if not path:
            return

        img = Image.open(path).resize((200, 200))
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        self.photo_data = bio.getvalue()

        self.photo = ImageTk.PhotoImage(img)
        self.photo_label.config(image=self.photo)

    # ================= CRUD =================
    def add_student(self):
        try:
            self.cursor.execute("""
                INSERT INTO students
                (student_id, fullname, grade, guardian, contact, rfid_uid, photo)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (
                self.student_id_var.get(),
                self.fullname_var.get(),
                self.grade_var.get(),
                self.guardian_name_var.get(),
                self.guardian_contact_var.get(),
                self.rfid_uid_var.get(),
                self.photo_data
            ))
            self.db.commit()
            messagebox.showinfo("Success", "Student added")
            self.fetch_students()
            self.clear_fields()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Duplicate", "Student ID or RFID already exists")

    def edit_student(self):
        self.cursor.execute("""
            UPDATE students SET
            fullname=%s, grade=%s, guardian=%s, contact=%s,
            rfid_uid=%s, photo=%s
            WHERE student_id=%s
        """, (
            self.fullname_var.get(),
            self.grade_var.get(),
            self.guardian_name_var.get(),
            self.guardian_contact_var.get(),
            self.rfid_uid_var.get(),
            self.photo_data,
            self.student_id_var.get()
        ))
        self.db.commit()
        messagebox.showinfo("Updated", "Student updated")
        self.fetch_students()

    def delete_student(self):
        self.cursor.execute(
            "DELETE FROM students WHERE student_id=%s",
            (self.student_id_var.get(),)
        )
        self.db.commit()
        self.fetch_students()
        self.clear_fields()

    def fetch_students(self):
        self.student_table.delete(*self.student_table.get_children())
        self.cursor.execute("SELECT student_id, fullname, grade FROM students")
        for row in self.cursor.fetchall():
            self.student_table.insert("", "end", values=row)

    def load_selected_student(self, event):
        selected = self.student_table.focus()
        if not selected:
            return

        sid = self.student_table.item(selected, "values")[0]
        self.cursor.execute("SELECT * FROM students WHERE student_id=%s", (sid,))
        row = self.cursor.fetchone()

        self.student_id_var.set(row[1])
        self.fullname_var.set(row[2])
        self.grade_var.set(row[3])
        self.guardian_name_var.set(row[4])
        self.guardian_contact_var.set(row[5])
        self.rfid_uid_var.set(row[6])
        self.photo_data = row[7]

        if self.photo_data:
            img = Image.open(io.BytesIO(self.photo_data)).resize((200, 200))
            self.photo = ImageTk.PhotoImage(img)
            self.photo_label.config(image=self.photo)

    def clear_fields(self):
        for var in [self.student_id_var, self.fullname_var, self.grade_var,
                    self.guardian_name_var, self.guardian_contact_var,
                    self.rfid_uid_var]:
            var.set("")
        self.photo_label.config(image="")
        self.photo_data = None


if __name__ == "__main__":
    root = tk.Tk()
    app = Student(root)
    root.mainloop()
