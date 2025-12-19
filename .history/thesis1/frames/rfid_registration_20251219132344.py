import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import ImageTk, Image
import sys, os

# Add parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.database import db_connect


class RfidRegistration(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg="#b2e5ed")
        self.root = root
        root.title("RFID MANAGEMENT SYSTEM - RFID REGISTRATION")
        root.geometry("1350x700+0+0")
        self.pack(fill="both", expand=True)

        # ================= HEADER =================
        self.title = tk.Frame(self, height=80, bg="#0047AB", bd=2, relief="groove")
        self.title.pack(fill="x")
        self.title.pack_propagate(False)

        tk.Label(
            self.title,
            text="RFID REGISTRATION",
            font=("Arial", 24, "bold"),
            bg="#0047AB",
            fg="white"
        ).place(x=50, y=20)

        # ================= FETCHER FRAME =================
        self.fetcher_frame = tk.Frame(self, width=500, height=330, bg="white", bd=2, relief="groove")
        self.fetcher_frame.place(x=70, y=100)
        self.fetcher_frame.pack_propagate(False)

        tk.Label(
            self.fetcher_frame,
            text="FETCHER INFORMATION",
            font=("Arial", 20, "bold"),
            bg="white",
            fg="#0047AB"
        ).place(x=20, y=10)

        self.fetcher_photo_frame = tk.Frame(
            self.fetcher_frame, width=200, height=200,
            bg="#E0E0E0", bd=2, relief="ridge"
        )
        self.fetcher_photo_frame.place(x=20, y=60)
        self.fetcher_photo_frame.pack_propagate(False)

        self.fetcher_photo_label = tk.Label(self.fetcher_photo_frame, bg="#E0E0E0")
        self.fetcher_photo_label.pack(fill="both", expand=True)

        tk.Button(
            self.fetcher_frame, text="Upload Photo",
            width=15, command=self.upload_photo
        ).place(x=60, y=270)

        self.rfid_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.contact_var = tk.StringVar()

        labels = ["RFID:", "Name:", "Address:", "Contact:"]
        vars_ = [self.rfid_var, self.name_var, self.address_var, self.contact_var]

        y = 80
        for lbl, var in zip(labels, vars_):
            tk.Label(self.fetcher_frame, text=lbl, font=("Arial", 14), bg="white").place(x=250, y=y)
            tk.Entry(self.fetcher_frame, textvariable=var, width=25, font=("Arial", 14)).place(x=330, y=y)
            y += 45

        # ================= STUDENT FRAME =================
        self.student_frame = tk.Frame(self, width=500, height=330, bg="white", bd=2, relief="groove")
        self.student_frame.place(x=780, y=100)
        self.student_frame.pack_propagate(False)

        tk.Label(
            self.student_frame,
            text="STUDENT INFORMATION",
            font=("Arial", 20, "bold"),
            bg="white",
            fg="#0047AB"
        ).place(x=20, y=10)

        self.student_photo_frame = tk.Frame(
            self.student_frame, width=200, height=200,
            bg="#E0E0E0", bd=2, relief="ridge"
        )
        self.student_photo_frame.place(x=20, y=60)
        self.student_photo_frame.pack_propagate(False)

        self.student_photo_label = tk.Label(self.student_photo_frame, bg="#E0E0E0")
        self.student_photo_label.pack(fill="both", expand=True)

        tk.Button(
            self.student_frame, text="Upload Photo",
            width=15, command=self.upload_photo
        ).place(x=60, y=270)

        self.student_id_var = tk.StringVar()
        self.student_name_var = tk.StringVar()
        self.grade_var = tk.StringVar()
        self.teacher_var = tk.StringVar()

        labels = ["Student ID:", "Name:", "Grade:", "Teacher:"]
        vars_ = [self.student_id_var, self.student_name_var, self.grade_var, self.teacher_var]

        y = 80
        for lbl, var in zip(labels, vars_):
            tk.Label(self.student_frame, text=lbl, font=("Arial", 14), bg="white").place(x=250, y=y)
            tk.Entry(self.student_frame, textvariable=var, width=25, font=("Arial", 14)).place(x=360, y=y)
            y += 45

        # ================= BUTTON BAR (IMPROVED) =================
        button_frame = tk.Frame(self, bg="#b2e5ed")
        button_frame.place(relx=0.5, y=460, anchor="center")

        btn_style = {
            "width": 14,
            "font": ("Arial", 14, "bold"),
            "fg": "white"
        }

        tk.Button(
            button_frame, text="ADD", bg="#4CAF50",
            command=self.add_record, **btn_style
        ).grid(row=0, column=0, padx=15)

        tk.Button(
            button_frame, text="EDIT", bg="#2196F3",
            command=self.edit_record, **btn_style
        ).grid(row=0, column=1, padx=15)

        tk.Button(
            button_frame, text="DELETE", bg="#F44336",
            command=self.delete_record, **btn_style
        ).grid(row=0, column=2, padx=15)

        # ================= TABLE =================
        columns = ("rfid", "fetcher_name", "student_id", "student_name", "grade", "teacher")
        self.table = ttk.Treeview(self, columns=columns, show="headings", height=6)
        self.table.place(x=70, y=520, width=1210)

        for col in columns:
            self.table.heading(col, text=col.replace("_", " ").title())
            self.table.column(col, width=180)

        self.table.bind("<<TreeviewSelect>>", self.load_selected)

        self.load_data()

    # ================= DATABASE =================
    def load_data(self):
        self.table.delete(*self.table.get_children())
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT rfid, fetcher_name, student_id, student_name, grade, teacher FROM registrations")
        for row in cursor.fetchall():
            self.table.insert("", "end", values=row)
        cursor.close()
        conn.close()

    def add_record(self):
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO registrations
            (rfid, fetcher_name, address, contact, student_id, student_name, grade, teacher)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            self.rfid_var.get(), self.name_var.get(),
            self.address_var.get(), self.contact_var.get(),
            self.student_id_var.get(), self.student_name_var.get(),
            self.grade_var.get(), self.teacher_var.get()
        ))
        conn.commit()
        cursor.close()
        conn.close()
        self.load_data()
        self.clear_fields()
        messagebox.showinfo("Success", "Record added successfully")

    def edit_record(self):
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE registrations SET
            fetcher_name=%s, address=%s, contact=%s,
            student_id=%s, student_name=%s, grade=%s, teacher=%s
            WHERE rfid=%s
        """, (
            self.name_var.get(), self.address_var.get(),
            self.contact_var.get(), self.student_id_var.get(),
            self.student_name_var.get(), self.grade_var.get(),
            self.teacher_var.get(), self.rfid_var.get()
        ))
        conn.commit()
        cursor.close()
        conn.close()
        self.load_data()
        self.clear_fields()

    def delete_record(self):
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM registrations WHERE rfid=%s", (self.rfid_var.get(),))
        conn.commit()
        cursor.close()
        conn.close()
        self.load_data()
        self.clear_fields()

    def load_selected(self, _):
        data = self.table.item(self.table.focus(), "values")
        if not data:
            return
        self.rfid_var.set(data[0])
        self.name_var.set(data[1])
        self.student_id_var.set(data[2])
        self.student_name_var.set(data[3])
        self.grade_var.set(data[4])
        self.teacher_var.set(data[5])

    def clear_fields(self):
        for var in (
            self.rfid_var, self.name_var, self.address_var, self.contact_var,
            self.student_id_var, self.student_name_var, self.grade_var, self.teacher_var
        ):
            var.set("")

    def upload_photo(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if not file_path:
            return
        img = Image.open(file_path).resize((200, 200))
        self.photo = ImageTk.PhotoImage(img)
        self.fetcher_photo_label.config(image=self.photo)
        self.fetcher_photo_label.image = self.photo


if __name__ == "__main__":
    root = tk.Tk()
    app = RfidRegistration(root)
    root.mainloop()
