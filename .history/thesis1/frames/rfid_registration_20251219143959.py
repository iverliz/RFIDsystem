import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os

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

        # ================= SEARCH BAR =================
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self, textvariable=self.search_var, width=30,
                                     font=("Arial", 15), fg="gray")
        self.search_entry.place(x=20, y=20)
        self.search_entry.insert(0, "Search")
        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<FocusOut>", self.add_placeholder)
        tk.Button(self, text="🔍", command=self.search).place(x=260, y=20)

        # ================= FETCHER FRAME =================
        self.fetcher_frame = tk.Frame(self, width=450, height=350, bg="white", bd=2, relief="groove")
        self.fetcher_frame.place(x=60, y=90)
        self.fetcher_frame.pack_propagate(False)

        tk.Label(self.fetcher_frame, text="FETCHER INFORMATION",
                 font=("Arial", 24, "bold"), bg="white", fg="#0047AB").place(x=20, y=20)

        self.rfid_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.contact_var = tk.StringVar()
        self.paired_rfid_var = tk.StringVar()

        fields = [
            ("RFID:", self.rfid_var, 80, 90),
            ("Name:", self.name_var, 120, 90),
            ("Address:", self.address_var, 160, 140),
            ("Contact:", self.contact_var, 200, 100),
            ("Paired RFID (Student):", self.paired_rfid_var, 240, 200),
        ]

        for text, var, y, x in fields:
            tk.Label(self.fetcher_frame, text=text, font=("Arial", 14), bg="white").place(x=20, y=y)
            tk.Entry(self.fetcher_frame, textvariable=var, font=("Arial", 14), width=30).place(x=x, y=y)

        # ================= STUDENT FRAME =================
        self.student_frame = tk.Frame(self, width=450, height=350, bg="white", bd=2, relief="groove")
        self.student_frame.place(x=850, y=90)
        self.student_frame.pack_propagate(False)

        tk.Label(self.student_frame, text="STUDENT INFORMATION",
                 font=("Arial", 24, "bold"), bg="white", fg="#0047AB").place(x=20, y=20)

        self.student_id_var = tk.StringVar()
        self.student_name_var = tk.StringVar()
        self.grade_var = tk.StringVar()
        self.teacher_var = tk.StringVar()

        fields = [
            ("Student ID:", self.student_id_var, 80),
            ("Name:", self.student_name_var, 120),
            ("Grade:", self.grade_var, 160),
            ("Teacher:", self.teacher_var, 200),
        ]

        for text, var, y in fields:
            tk.Label(self.student_frame, text=text, font=("Arial", 14), bg="white").place(x=20, y=y)
            tk.Entry(self.student_frame, textvariable=var, font=("Arial", 14), width=30).place(x=160, y=y)

        # ================= BUTTONS =================
        tk.Button(self, text="ADD", width=12, font=("Arial", 14, "bold"),
                  bg="#4CAF50", fg="white", command=self.add_record).place(x=480, y=470)

        tk.Button(self, text="EDIT", width=12, font=("Arial", 14, "bold"),
                  bg="#2196F3", fg="white", command=self.edit_record).place(x=630, y=470)

        tk.Button(self, text="DELETE", width=12, font=("Arial", 14, "bold"),
                  bg="#F44336", fg="white", command=self.delete_record).place(x=780, y=470)

        # ================= TABLE =================
        columns = (
            "rfid", "fetcher_name", "student_id",
            "student_name", "grade", "teacher", "paired_rfid"
        )

        self.table = ttk.Treeview(self, columns=columns, show="headings", height=6)
        self.table.place(x=200, y=540, width=1200)

        for col in columns:
            self.table.heading(col, text=col.replace("_", " ").title())
            self.table.column(col, width=160)

        self.table.bind("<<TreeviewSelect>>", self.load_selected)
    

    # ================= DATABASE =================
    def load_data(self):
        self.table.delete(*self.table.get_children())
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT rfid, fetcher_name, student_id,
                       student_name, grade, teacher, paired_rfid
                FROM registrations
            """)
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
                (rfid, fetcher_name, address, contact,
                 student_id, student_name, grade, teacher, paired_rfid)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                self.rfid_var.get(), self.name_var.get(),
                self.address_var.get(), self.contact_var.get(),
                self.student_id_var.get(), self.student_name_var.get(),
                self.grade_var.get(), self.teacher_var.get(),
                self.paired_rfid_var.get()
            ))
            conn.commit()
            messagebox.showinfo("Success", "Record added successfully")
            self.load_data()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
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
                student_id=%s, student_name=%s, grade=%s,
                teacher=%s, paired_rfid=%s
                WHERE rfid=%s
            """, (
                self.name_var.get(), self.address_var.get(),
                self.contact_var.get(), self.student_id_var.get(),
                self.student_name_var.get(), self.grade_var.get(),
                self.teacher_var.get(), self.paired_rfid_var.get(),
                self.rfid_var.get()
            ))
            conn.commit()
            self.load_data()
            self.clear_fields()
        finally:
            cursor.close()
            conn.close()

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
        (
            self.rfid_var.set(data[0]),
            self.name_var.set(data[1]),
            self.student_id_var.set(data[2]),
            self.student_name_var.set(data[3]),
            self.grade_var.set(data[4]),
            self.teacher_var.set(data[5]),
            self.paired_rfid_var.set(data[6])
        )

    def clear_fields(self):
        for var in (
            self.rfid_var, self.name_var, self.address_var, self.contact_var,
            self.student_id_var, self.student_name_var,
            self.grade_var, self.teacher_var, self.paired_rfid_var
        ):
            var.set("")

    # ================= SEARCH =================
    def search(self):
        keyword = f"%{self.search_var.get()}%"
        self.table.delete(*self.table.get_children())
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT rfid, fetcher_name, student_id,
                   student_name, grade, teacher, paired_rfid
            FROM registrations
            WHERE rfid LIKE %s OR fetcher_name LIKE %s
               OR student_name LIKE %s OR paired_rfid LIKE %s
        """, (keyword, keyword, keyword, keyword))
        for row in cursor.fetchall():
            self.table.insert("", "end", values=row)
        cursor.close()
        conn.close()

    def clear_placeholder(self, _):
        if self.search_entry.get() == "Search":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="black")

    def add_placeholder(self, _):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search")
            self.search_entry.config(fg="gray")


if __name__ == "__main__":
    root = tk.Tk()
    app = RfidRegistration(root)
    root.mainloop()
