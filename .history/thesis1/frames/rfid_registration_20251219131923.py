import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import os, sys

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
        header = tk.Frame(self, bg="#0047AB", height=80)
        header.pack(fill="x")

        tk.Label(
            header, text="RFID REGISTRATION",
            font=("Arial", 24, "bold"),
            bg="#0047AB", fg="white"
        ).pack(side="left", padx=30, pady=20)

        # ================= FETCHER FRAME =================
        self.fetcher_frame = tk.Frame(self, bg="white", bd=2, relief="groove")
        self.fetcher_frame.place(x=50, y=100, width=500, height=320)

        tk.Label(
            self.fetcher_frame, text="FETCHER INFORMATION",
            font=("Arial", 18, "bold"), bg="white", fg="#0047AB"
        ).place(x=20, y=10)

        # Fetcher photo
        self.fetcher_photo_label = tk.Label(
            self.fetcher_frame, bg="#E0E0E0", width=20, height=10
        )
        self.fetcher_photo_label.place(x=20, y=50)

        tk.Button(
            self.fetcher_frame, text="Upload Photo",
            command=lambda: self.upload_photo(self.fetcher_photo_label)
        ).place(x=60, y=220)

        # Fetcher fields
        self.rfid_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.contact_var = tk.StringVar()

        labels = ["RFID", "Name", "Address", "Contact"]
        vars_ = [self.rfid_var, self.name_var, self.address_var, self.contact_var]

        y = 60
        for lbl, var in zip(labels, vars_):
            tk.Label(self.fetcher_frame, text=lbl, bg="white", font=("Arial", 12)).place(x=240, y=y)
            tk.Entry(self.fetcher_frame, textvariable=var, width=25).place(x=320, y=y)
            y += 40

        # ================= STUDENT FRAME =================
        self.student_frame = tk.Frame(self, bg="white", bd=2, relief="groove")
        self.student_frame.place(x=780, y=100, width=500, height=320)

        tk.Label(
            self.student_frame, text="STUDENT INFORMATION",
            font=("Arial", 18, "bold"), bg="white", fg="#0047AB"
        ).place(x=20, y=10)

        self.student_photo_label = tk.Label(
            self.student_frame, bg="#E0E0E0", width=20, height=10
        )
        self.student_photo_label.place(x=20, y=50)

        tk.Button(
            self.student_frame, text="Upload Photo",
            command=lambda: self.upload_photo(self.student_photo_label)
        ).place(x=60, y=220)

        self.student_id_var = tk.StringVar()
        self.student_name_var = tk.StringVar()
        self.grade_var = tk.StringVar()
        self.teacher_var = tk.StringVar()

        labels = ["Student ID", "Name", "Grade", "Teacher"]
        vars_ = [self.student_id_var, self.student_name_var, self.grade_var, self.teacher_var]

        y = 60
        for lbl, var in zip(labels, vars_):
            tk.Label(self.student_frame, text=lbl, bg="white", font=("Arial", 12)).place(x=240, y=y)
            tk.Entry(self.student_frame, textvariable=var, width=25).place(x=350, y=y)
            y += 40

        # ================= BUTTONS =================
        tk.Button(self, text="ADD", width=12, bg="#4CAF50",
                  fg="white", command=self.add_record).place(x=450, y=450)

        tk.Button(self, text="EDIT", width=12, bg="#2196F3",
                  fg="white", command=self.edit_record).place(x=600, y=450)

        tk.Button(self, text="DELETE", width=12, bg="#F44336",
                  fg="white", command=self.delete_record).place(x=750, y=450)

        # ================= SEARCH =================
        self.search_var = tk.StringVar()
        tk.Entry(self, textvariable=self.search_var, width=30).place(x=50, y=500)
        tk.Button(self, text="Search", command=self.search).place(x=300, y=497)

        # ================= TABLE =================
        columns = (
            "rfid", "fetcher_name", "address", "contact",
            "student_id", "student_name", "grade", "teacher"
        )

        self.table = ttk.Treeview(self, columns=columns, show="headings", height=6)
        self.table.place(x=50, y=540, width=1250)

        for col in columns:
            self.table.heading(col, text=col.replace("_", " ").title())
            self.table.column(col, width=150)

        self.table.bind("<<TreeviewSelect>>", self.load_selected)

        self.load_data()

    # ================= PHOTO =================
    def upload_photo(self, label):
        filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        messagebox.showinfo("Info", "Photo upload connected (display optional)")

    # ================= DATABASE =================
    def load_data(self):
        self.table.delete(*self.table.get_children())
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM registrations")
            for row in cursor.fetchall():
                self.table.insert("", "end", values=row)
        finally:
            cursor.close()
            conn.close()

    def add_record(self):
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO registrations
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                self.rfid_var.get(), self.name_var.get(),
                self.address_var.get(), self.contact_var.get(),
                self.student_id_var.get(), self.student_name_var.get(),
                self.grade_var.get(), self.teacher_var.get()
            ))
            conn.commit()
            self.load_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Record added")
        finally:
            cursor.close()
            conn.close()

    def edit_record(self):
        try:
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
            self.load_data()
            self.clear_fields()
        finally:
            cursor.close()
            conn.close()

    def delete_record(self):
        if not messagebox.askyesno("Confirm", "Delete this record?"):
            return
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM registrations WHERE rfid=%s", (self.rfid_var.get(),))
        conn.commit()
        cursor.close()
        conn.close()
        self.load_data()
        self.clear_fields()

    def search(self):
        keyword = f"%{self.search_var.get()}%"
        self.table.delete(*self.table.get_children())
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM registrations
            WHERE rfid LIKE %s OR fetcher_name LIKE %s OR student_name LIKE %s
        """, (keyword, keyword, keyword))
        for row in cursor.fetchall():
            self.table.insert("", "end", values=row)
        cursor.close()
        conn.close()

    def load_selected(self, _):
        data = self.table.item(self.table.focus(), "values")
        if not data:
            return
        (
            self.rfid_var.set(data[0]),
            self.name_var.set(data[1]),
            self.address_var.set(data[2]),
            self.contact_var.set(data[3]),
            self.student_id_var.set(data[4]),
            self.student_name_var.set(data[5]),
            self.grade_var.set(data[6]),
            self.teacher_var.set(data[7])
        )

    def clear_fields(self):
        for var in (
            self.rfid_var, self.name_var, self.address_var, self.contact_var,
            self.student_id_var, self.student_name_var, self.grade_var, self.teacher_var
        ):
            var.set("")


if __name__ == "__main__":
    root = tk.Tk()
    app = RfidRegistration(root)
    root.mainloop()
