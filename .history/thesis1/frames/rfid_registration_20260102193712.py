import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os

# ================= PATH SETUP =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.database import db_connect


class RfidRegistration(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg="#b2e5ed")
        self.root = root
        root.title("RFID MANAGEMENT SYSTEM - RFID REGISTRATION")
        root.geometry("1350x700+0+0")
        self.pack(fill="both", expand=True)

        # ================= RFID SESSION STATE =================
        self.tap_stage = "fetcher"   # fetcher → student
        self.fetcher_uid = None
        self.student_uid = None
        self.rfid_buffer = ""
        self.rfid_timer = None

        # ================= SEARCH =================
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            self, textvariable=self.search_var,
            font=("Arial", 15), width=30, fg="gray"
        )
        self.search_entry.place(x=450, y=20)
        self.search_entry.insert(0, "Search")
        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<FocusOut>", self.add_placeholder)

        tk.Button(self, text="🔍", command=self.search).place(x=780, y=20)

        # ================= FRAMES =================
        FRAME_WIDTH = 500
        FRAME_HEIGHT = 330
        FRAME_Y = 80

        # ================= FETCHER FRAME =================
        self.fetcher_frame = tk.Frame(
            self, width=FRAME_WIDTH, height=FRAME_HEIGHT,
            bg="white", bd=2, relief="groove"
        )
        self.fetcher_frame.place(x=80, y=FRAME_Y)
        self.fetcher_frame.pack_propagate(False)

        tk.Label(
            self.fetcher_frame, text="FETCHER INFORMATION",
            font=("Arial", 22, "bold"), bg="white", fg="#0047AB"
        ).pack(pady=10)

        self.rfid_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.contact_var = tk.StringVar()

        fetcher_fields = [
            ("RFID:", self.rfid_var, True),
            ("Name:", self.name_var, False),
            ("Address:", self.address_var, False),
            ("Contact:", self.contact_var, False),
        ]

        y = 60
        for label, var, readonly in fetcher_fields:
            tk.Label(
                self.fetcher_frame, text=label,
                font=("Arial", 13), bg="white"
            ).place(x=20, y=y)

            tk.Entry(
                self.fetcher_frame,
                textvariable=var,
                font=("Arial", 13),
                width=30,
                state="readonly" if readonly else "normal"
            ).place(x=200, y=y)

            y += 45

        # ================= STUDENT FRAME =================
        self.student_frame = tk.Frame(
            self, width=FRAME_WIDTH, height=FRAME_HEIGHT,
            bg="white", bd=2, relief="groove"
        )
        self.student_frame.place(x=760, y=FRAME_Y)
        self.student_frame.pack_propagate(False)

        tk.Label(
            self.student_frame, text="STUDENT INFORMATION",
            font=("Arial", 22, "bold"), bg="white", fg="#0047AB"
        ).pack(pady=10)

        self.student_id_var = tk.StringVar()
        self.student_name_var = tk.StringVar()
        self.grade_var = tk.StringVar()
        self.teacher_var = tk.StringVar()
        self.paired_rfid_var = tk.StringVar()

        student_fields = [
            ("Student RFID:", self.paired_rfid_var, True),
            ("Student ID:", self.student_id_var, False),
            ("Name:", self.student_name_var, False),
            ("Grade:", self.grade_var, False),
            ("Teacher:", self.teacher_var, False),
        ]

        y = 60
        for label, var, readonly in student_fields:
            tk.Label(
                self.student_frame, text=label,
                font=("Arial", 13), bg="white"
            ).place(x=20, y=y)

            tk.Entry(
                self.student_frame,
                textvariable=var,
                font=("Arial", 13),
                width=30,
                state="readonly" if readonly else "normal"
            ).place(x=200, y=y)

            y += 45

        # ================= BUTTONS =================
        btn_y = FRAME_Y + FRAME_HEIGHT + 20
        btn_x = 1350 // 2 - 220

        tk.Button(
            self, text="ADD", width=12,
            font=("Arial", 14, "bold"),
            bg="#4CAF50", fg="white",
            command=self.add_record
        ).place(x=btn_x, y=btn_y)

        tk.Button(
            self, text="EDIT", width=12,
            font=("Arial", 14, "bold"),
            bg="#2196F3", fg="white",
            command=self.edit_record
        ).place(x=btn_x + 150, y=btn_y)

        tk.Button(
            self, text="DELETE", width=12,
            font=("Arial", 14, "bold"),
            bg="#F44336", fg="white",
            command=self.delete_record
        ).place(x=btn_x + 300, y=btn_y)

        # ================= TABLE =================
        columns = (
            "rfid", "fetcher_name", "address", "contact",
            "student_id", "student_name", "grade",
            "teacher", "paired_rfid"
        )

        self.table = ttk.Treeview(
            self, columns=columns,
            show="headings", height=7
        )
        self.table.place(x=100, y=btn_y + 70, width=1150)

        for col in columns:
            self.table.heading(col, text=col.replace("_", " ").title())
            self.table.column(col, width=120, anchor="center")

        self.table.bind("<<TreeviewSelect>>", self.load_selected)

        # ================= RFID LISTENER =================
        self.root.bind_all("<Key>", self.capture_rfid)

        self.load_data()

    # ================= RFID AUTO READ =================
    def capture_rfid(self, event):
        if not event.char.isalnum():
            return

        self.rfid_buffer += event.char

        if self.rfid_timer:
            self.root.after_cancel(self.rfid_timer)

        self.rfid_timer = self.root.after(300, self.process_rfid)

    def process_rfid(self):
        uid = self.rfid_buffer.strip()
        self.rfid_buffer = ""

        if not uid:
            return

        if self.tap_stage == "fetcher":
            self.fetcher_uid = uid
            self.rfid_var.set(uid)
            self.match_rfid(uid, "fetcher")
            messagebox.showinfo("RFID", "Fetcher RFID scanned")
            self.tap_stage = "student"
        else:
            self.student_uid = uid
            self.paired_rfid_var.set(uid)
            self.match_rfid(uid, "student")
            messagebox.showinfo("RFID", "Student RFID scanned")
            self.tap_stage = "fetcher"

    # ================= DATABASE =================
    def match_rfid(self, uid, role):
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT rfid, fetcher_name, address, contact,
                       student_id, student_name, grade,
                       teacher, paired_rfid
                FROM registrations
                WHERE rfid=%s OR paired_rfid=%s
            """, (uid, uid))
            row = cursor.fetchone()
            if not row:
                return

            _, name, addr, contact, sid, sname, grade, teacher, _ = row

            if role == "fetcher":
                self.name_var.set(name)
                self.address_var.set(addr)
                self.contact_var.set(contact)
            else:
                self.student_id_var.set(sid)
                self.student_name_var.set(sname)
                self.grade_var.set(grade)
                self.teacher_var.set(teacher)

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def load_data(self):
        self.table.delete(*self.table.get_children())
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM registrations")
            for row in cursor.fetchall():
                self.table.insert("", "end", values=row)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def add_record(self):
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO registrations
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                self.rfid_var.get(), self.name_var.get(),
                self.address_var.get(), self.contact_var.get(),
                self.student_id_var.get(), self.student_name_var.get(),
                self.grade_var.get(), self.teacher_var.get(),
                self.paired_rfid_var.get()
            ))
            conn.commit()
            self.load_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Record added")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def edit_record(self):
        pass

    def delete_record(self):
        pass

    # ================= HELPERS =================
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
            self.teacher_var.set(data[7]),
            self.paired_rfid_var.set(data[8])
        )

    def clear_fields(self):
        for var in (
            self.rfid_var, self.name_var, self.address_var,
            self.contact_var, self.student_id_var,
            self.student_name_var, self.grade_var,
            self.teacher_var, self.paired_rfid_var
        ):
            var.set("")

    def search(self):
        pass

    def clear_placeholder(self, _):
        if self.search_entry.get() == "Search":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="black")

    def add_placeholder(self, _):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search")
            self.search_entry.config(fg="gray")


# ================= RUN =================
if __name__ == "__main__":
    root = tk.Tk()
    app = RfidRegistration(root)
    root.mainloop()
