import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os

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
        self.search_entry = tk.Entry(self, textvariable=self.search_var, width=30, font=("Arial", 15))
        self.search_entry.place(x=20, y=20)
        tk.Button(self, text="🔍", command=self.search).place(x=260, y=20)

        # ================= FETCHER FRAME =================
        self.fetcher_frame = tk.Frame(self, width=450, height=350, bg="white", bd=2, relief="groove")
        self.fetcher_frame.place(x=60, y=90)

        tk.Label(self.fetcher_frame, text="FETCHER INFORMATION",
                 font=("Arial", 24, "bold"), bg="white", fg="#0047AB").place(x=20, y=20)

        self.rfid_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.contact_var = tk.StringVar()
        self.paired_rfid_var = tk.StringVar()

        labels = ["RFID:", "Name:", "Address:", "Contact:", "Paired RFID (Student):"]
        vars_ = [self.rfid_var, self.name_var, self.address_var,
                 self.contact_var, self.paired_rfid_var]

        y = 80
        for label, var in zip(labels, vars_):
            tk.Label(self.fetcher_frame, text=label, bg="white", font=("Arial", 14)).place(x=20, y=y)
            tk.Entry(self.fetcher_frame, textvariable=var, width=30, font=("Arial", 14)).place(x=180, y=y)
            y += 40

        # ================= STUDENT FRAME =================
        self.student_frame = tk.Frame(self, width=450, height=350, bg="white", bd=2, relief="groove")
        self.student_frame.place(x=850, y=90)

        tk.Label(self.student_frame, text="STUDENT INFORMATION",
                 font=("Arial", 24, "bold"), bg="white", fg="#0047AB").place(x=20, y=20)

        self.student_id_var = tk.StringVar()
        self.student_name_var = tk.StringVar()
        self.grade_var = tk.StringVar()
        self.teacher_var = tk.StringVar()

        labels = ["Student ID:", "Name:", "Grade:", "Teacher:"]
        vars_ = [self.student_id_var, self.student_name_var,
                 self.grade_var, self.teacher_var]

        y = 80
        for label, var in zip(labels, vars_):
            tk.Label(self.student_frame, text=label, bg="white", font=("Arial", 14)).place(x=20, y=y)
            tk.Entry(self.student_frame, textvariable=var, width=30, font=("Arial", 14)).place(x=160, y=y)
            y += 40

        # ================= BUTTONS =================
        tk.Button(self, text="ADD", width=12, bg="#4CAF50", fg="white",
                  font=("Arial", 14, "bold"), command=self.add_record).place(x=480, y=470)

        tk.Button(self, text="DELETE", width=12, bg="#F44336", fg="white",
                  font=("Arial", 14, "bold"), command=self.delete_record).place(x=780, y=470)

        # ================= TABLE =================
        columns = ("rfid", "fetcher", "student_id", "student", "grade", "teacher", "paired_rfid")
        self.table = ttk.Treeview(self, columns=columns, show="headings", height=6)
        self.table.place(x=200, y=540, width=1200)

        for col in columns:
            self.table.heading(col, text=col.replace("_", " ").title())
            self.table.column(col, width=150)

        self.table.bind("<<TreeviewSelect>>", self.load_selected)
        self.load_data()

    # ================= DATABASE =================
    def load_data(self):
        self.table.delete(*self.table.get_children())
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT rfid, fetcher_name, student_id, student_name, grade, teacher, paired_rfid
            FROM registrations
        """)
        for row in cursor.fetchall():
            self.table.insert("", "end", values=row)
        cursor.close()
        conn.close()

    def add_record(self):
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO registrations
            (rfid, fetcher_name, address, contact,
             student_id, student_name, grade, teacher, paired_rfid)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            self.rfid_var.get(), self.name_var.get(), self.address_var.get(),
            self.contact_var.get(), self.student_id_var.get(),
            self.student_name_var.get(), self.grade_var.get(),
            self.teacher_var.get(), self.paired_rfid_var.get()
        ))
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Success", "Record Added")
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

    def load_selected(self, event):
        data = self.table.item(self.table.focus(), "values")
        if not data:
            return
        (self.rfid_var.set(data[0]), self.name_var.set(data[1]),
         self.student_id_var.set(data[2]), self.student_name_var.set(data[3]),
         self.grade_var.set(data[4]), self.teacher_var.set(data[5]),
         self.paired_rfid_var.set(data[6]))

    def clear_fields(self):
        for var in (
            self.rfid_var, self.name_var, self.address_var,
            self.contact_var, self.student_id_var,
            self.student_name_var, self.grade_var,
            self.teacher_var, self.paired_rfid_var
        ):
            var.set("")

    def search(self):
        keyword = f"%{self.search_var.get()}%"
        self.table.delete(*self.table.get_children())
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT rfid, fetcher_name, student_id, student_name, grade, teacher, paired_rfid
            FROM registrations
            WHERE rfid LIKE %s OR fetcher_name LIKE %s
               OR student_name LIKE %s OR paired_rfid LIKE %s
        """, (keyword, keyword, keyword, keyword))
        for row in cursor.fetchall():
            self.table.insert("", "end", values=row)
        cursor.close()
        conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    RfidRegistration(root)
    root.mainloop()
