import tkinter as tk
from tkinter import messagebox, ttk
import sys, os
import serial, threading, time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from utils.database import db_connect


class RfidRegistration(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#b2e5ed")
        self.controller = controller
        self.pack(fill="both", expand=True)

        self.scan_stage = "fetcher"

        # ================= SERIAL =================
        try:
            self.ser = serial.Serial("COM3", 9600, timeout=1)
            time.sleep(2)
            threading.Thread(target=self.read_serial, daemon=True).start()
        except Exception as e:
            messagebox.showwarning("RFID", f"RFID reader not detected:\n{e}")
            self.ser = None

        # ================= HEADER =================
        header = tk.Frame(self, bg="#0047AB", height=65)
        header.pack(fill="x")

        tk.Label(
            header, text="RFID REGISTRATION",
            font=("Arial", 20, "bold"),
            bg="#0047AB", fg="white"
        ).pack(side="left", padx=20, pady=15)

        # ================= SEARCH =================
        search_frame = tk.Frame(self, bg="#b2e5ed")
        search_frame.pack(fill="x", padx=15, pady=5)

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                     font=("Arial", 13), width=30, fg="gray")
        self.search_entry.insert(0, "Search")
        self.search_entry.pack(side="right", padx=5)
        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<FocusOut>", self.add_placeholder)

        tk.Button(search_frame, text="🔍", command=self.search).pack(side="right")

        # ================= VARIABLES =================
        self.rfid_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.contact_var = tk.StringVar()
        self.paired_rfid_var = tk.StringVar()

        self.student_rfid_var = tk.StringVar()
        self.student_name_var = tk.StringVar()
        self.grade_var = tk.StringVar()
        self.teacher_var = tk.StringVar()
        self.student_id_var = tk.StringVar()

        # ================= FORMS =================
        forms = tk.Frame(self, bg="#b2e5ed")
        forms.pack(padx=15, pady=5)
        forms.columnconfigure((0, 1), weight=1)

        self.fetcher_frame = self.create_form(
            forms, "FETCHER INFORMATION",
            [("Fetcher RFID", self.rfid_var),
             ("Name", self.name_var),
             ("Address", self.address_var),
             ("Contact", self.contact_var),
             ("Paired RFID", self.paired_rfid_var)],
            0
        )

        self.student_frame = self.create_form(
            forms, "STUDENT INFORMATION",
            [("Student RFID", self.student_rfid_var),
             ("Student ID", self.student_id_var),
             ("Name", self.student_name_var),
             ("Grade", self.grade_var),
             ("Teacher", self.teacher_var)],
            1
        )

        # ================= BUTTONS =================
        btn_frame = tk.Frame(self, bg="#b2e5ed")
        btn_frame.pack(pady=5)

        for txt, clr, cmd in (
            ("ADD", "#4CAF50", self.add_record),
            ("EDIT", "#2196F3", self.edit_record),
            ("DELETE", "#F44336", self.delete_record),
        ):
            tk.Button(
                btn_frame, text=txt, bg=clr, fg="white",
                font=("Arial", 12, "bold"), width=12, command=cmd
            ).pack(side="left", padx=5)

        # ================= TABLE =================
        table_frame = tk.Frame(self, bg="white", bd=2, relief="groove")
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("rfid", "fetcher_name", "student_rfid", "address", "contact",
                   "student_id", "student_name", "grade", "teacher", "paired_rfid")

        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
        self.table.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        scrollbar.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=scrollbar.set)

        for col in columns:
            self.table.heading(col, text=col.replace("_", " ").title())
            self.table.column(col, width=120, anchor="center")

        self.table.bind("<<TreeviewSelect>>", self.load_selected)
        self.load_data()

    # ================= FORM CREATOR =================
    def create_form(self, parent, title, fields, col):
        frame = tk.Frame(parent, bg="white", bd=2, relief="groove", padx=10, pady=5)
        frame.grid(row=0, column=col, padx=10, pady=5, sticky="n")

        tk.Label(frame, text=title, font=("Arial", 16, "bold"),
                 bg="white", fg="#0047AB").pack(pady=5)

        for label, var in fields:
            row = tk.Frame(frame, bg="white")
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label + ":", bg="white", width=14, anchor="w").pack(side="left")
            tk.Entry(row, textvariable=var, font=("Arial", 12)).pack(side="right", fill="x", expand=True)

        return frame

    # ================= SERIAL =================
    def read_serial(self):
        while self.ser and self.ser.is_open:
            try:
                uid = self.ser.readline().decode(errors="ignore").strip()
                if uid:
                    self.after(0, self.process_uid, uid.split(":")[-1])
            except Exception:
                pass

    def process_uid(self, uid):
        if self.scan_stage == "fetcher":
            if self.check_duplicate_rfid(uid):
                messagebox.showerror("Duplicate", "Fetcher RFID already exists")
                return
            self.rfid_var.set(uid)
            self.scan_stage = "student"
            messagebox.showinfo("Next", "Scan STUDENT RFID")
        else:
            self.student_rfid_var.set(uid)
            self.paired_rfid_var.set(uid)
            self.scan_stage = "fetcher"
            messagebox.showinfo("Ready", "You may now ADD record")

    # ================= DATABASE =================
    def load_data(self):
        self.table.delete(*self.table.get_children())
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT rfid, fetcher_name, student_rfid, address, contact,
                       student_id, student_name, grade, teacher, paired_rfid
                FROM registrations
            """)
            for row in cursor.fetchall():
                self.table.insert("", "end", values=row)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def check_duplicate_rfid(self, uid):
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT rfid FROM registrations WHERE rfid=%s", (uid,))
            return cursor.fetchone() is not None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # ================= CRUD =================
    def add_record(self):
        if not self.rfid_var.get() or not self.student_rfid_var.get():
            messagebox.showwarning("Missing", "Scan both RFIDs")
            return
        self.execute_db("""
            INSERT INTO registrations
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            self.rfid_var.get(), self.name_var.get(),
            self.student_rfid_var.get(), self.address_var.get(),
            self.contact_var.get(), self.student_id_var.get(),
            self.student_name_var.get(), self.grade_var.get(),
            self.teacher_var.get(), self.paired_rfid_var.get()
        ), "Added")

    def edit_record(self):
        self.execute_db("""
            UPDATE registrations SET
            fetcher_name=%s, student_rfid=%s, address=%s, contact=%s,
            student_id=%s, student_name=%s, grade=%s, teacher=%s, paired_rfid=%s
            WHERE rfid=%s
        """, (
            self.name_var.get(), self.student_rfid_var.get(),
            self.address_var.get(), self.contact_var.get(),
            self.student_id_var.get(), self.student_name_var.get(),
            self.grade_var.get(), self.teacher_var.get(),
            self.paired_rfid_var.get(), self.rfid_var.get()
        ), "Updated")

    def delete_record(self):
        if not messagebox.askyesno("Confirm", "Delete record?"):
            return
        self.execute_db(
            "DELETE FROM registrations WHERE rfid=%s",
            (self.rfid_var.get(),), "Deleted"
        )

    def execute_db(self, query, values, msg):
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            messagebox.showinfo(msg, f"Record {msg.lower()}")
            self.load_data()
            self.clear_fields()
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # ================= UTIL =================
    def load_selected(self, _):
        data = self.table.item(self.table.focus(), "values")
        if not data:
            return
        (self.rfid_var.set(data[0]), self.name_var.set(data[1]),
         self.student_rfid_var.set(data[2]), self.address_var.set(data[3]),
         self.contact_var.set(data[4]), self.student_id_var.set(data[5]),
         self.student_name_var.set(data[6]), self.grade_var.set(data[7]),
         self.teacher_var.set(data[8]), self.paired_rfid_var.set(data[9]))

    def clear_fields(self):
        for v in (self.rfid_var, self.name_var, self.address_var, self.contact_var,
                  self.student_rfid_var, self.student_id_var, self.student_name_var,
                  self.grade_var, self.teacher_var, self.paired_rfid_var):
            v.set("")
        self.scan_stage = "fetcher"

    def clear_placeholder(self, _):
        if self.search_entry.get() == "Search":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="black")

    def add_placeholder(self, _):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search")
            self.search_entry.config(fg="gray")

    def search(self):
        key = "%" + self.search_var.get() + "%"
        self.table.delete(*self.table.get_children())
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM registrations
                WHERE rfid LIKE %s OR fetcher_name LIKE %s
                OR student_name LIKE %s OR paired_rfid LIKE %s
            """, (key, key, key, key))
            for row in cursor.fetchall():
                self.table.insert("", "end", values=row)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
