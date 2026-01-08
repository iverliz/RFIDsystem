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
        self.selected_id = None  # store registration_id of selected row

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

        columns = ("regirstration_id", "rfid", "fetcher_name", "student_rfid", "address", "contact",
                   "student_id", "student_name", "grade", "teacher", "paired_rfid")

        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
        self.table.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        scrollbar.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=scrollbar.set)

        for col in columns:
            self.table.heading(col, text=col.replace("_", " ").title())
            self.table.column(col, width=120, anchor="center")
        self.table.column("id", width=0, stretch=False)  # hide ID column

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
                time.sleep(0.1)
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
        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT registration_id, rfid, fetcher_name, student_rfid, address, contact,
                           student_id, student_name, grade, teacher, paired_rfid
                    FROM registrations
                """)
                for row in cursor.fetchall():
                    self.table.insert("", "end", values=row)

    def check_duplicate_rfid(self, uid):
        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 1 FROM registrations WHERE rfid=%s OR student_rfid=%s
                """, (uid, uid))
                return cursor.fetchone() is not None

    # ================= CRUD =================
    def add_record(self):
        if not all([self.rfid_var.get(), self.student_rfid_var.get(),
                    self.name_var.get(), self.student_name_var.get()]):
            messagebox.showwarning("Missing", "All fields are required")
            return

        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO registrations
                    (rfid, fetcher_name, student_rfid, address, contact,
                     student_id, student_name, grade, teacher, paired_rfid)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (self.rfid_var.get(), self.name_var.get(),
                      self.student_rfid_var.get(), self.address_var.get(),
                      self.contact_var.get(), self.student_id_var.get(),
                      self.student_name_var.get(), self.grade_var.get(),
                      self.teacher_var.get(), self.paired_rfid_var.get()))
                conn.commit()
        messagebox.showinfo("Added", "Record added successfully")
        self.load_data()
        self.clear_fields()

    def edit_record(self):
        if not self.selected_id:
            messagebox.showwarning("Select", "Select a record to edit")
            return

        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE registrations SET
                        fetcher_name=%s, student_rfid=%s, address=%s, contact=%s,
                        student_id=%s, student_name=%s, grade=%s, teacher=%s, paired_rfid=%s
                    WHERE registration_id=%s
                """, (self.name_var.get(), self.student_rfid_var.get(),
                      self.address_var.get(), self.contact_var.get(),
                      self.student_id_var.get(), self.student_name_var.get(),
                      self.grade_var.get(), self.teacher_var.get(),
                      self.paired_rfid_var.get(), self.selected_id))
                conn.commit()
        messagebox.showinfo("Updated", "Record updated successfully")
        self.load_data()
        self.clear_fields()

    def delete_record(self):
        if not self.selected_id:
            messagebox.showwarning("Select", "Select a record to delete")
            return
        if not messagebox.askyesno("Confirm", "Delete record?"):
            return
        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM registrations WHERE registration_id=%s", (self.selected_id,))
                conn.commit()
        messagebox.showinfo("Deleted", "Record deleted successfully")
        self.load_data()
        self.clear_fields()
        self.table.selection_remove(self.table.focus())

    # ================= UTIL =================
    def load_selected(self, _):
        data = self.table.item(self.table.focus(), "values")
        if not data:
            return
        (self.selected_, self.rfid_var.set(data[1]), self.name_var.set(data[2]),
         self.student_rfid_var.set(data[3]), self.address_var.set(data[4]),
         self.contact_var.set(data[5]), self.student_id_var.set(data[6]),
         self.student_name_var.set(data[7]), self.grade_var.set(data[8]),
         self.teacher_var.set(data[9]), self.paired_rfid_var.set(data[10]))

    def clear_fields(self):
        for v in (self.rfid_var, self.name_var, self.address_var, self.contact_var,
                  self.student_rfid_var, self.student_id_var, self.student_name_var,
                  self.grade_var, self.teacher_var, self.paired_rfid_var):
            v.set("")
        self.selected_id = None
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
        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT  rfid, fetcher_name, student_rfid, address, contact,
                           student_id, student_name, grade, teacher, paired_rfid
                    FROM registrations
                    WHERE rfid LIKE %s OR fetcher_name LIKE %s
                        OR student_name LIKE %s OR student_id LIKE %s
                        OR grade LIKE %s OR teacher LIKE %s OR paired_rfid LIKE %s
                """, (key, key, key, key, key, key, key))
                for row in cursor.fetchall():
                    self.table.insert("", "end", values=row)
