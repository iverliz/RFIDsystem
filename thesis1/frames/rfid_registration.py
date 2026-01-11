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
        self.selected_registration_id = None

        # ================= PAGINATION =================
        self.page_size = 10
        self.current_page = 1
        self.total_records = 0
        self.total_pages = 1
        self.is_searching = False

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

        tk.Label(header, text="RFID REGISTRATION",
                 font=("Arial", 20, "bold"),
                 bg="#0047AB", fg="white").pack(side="left", padx=20, pady=15)

        # ================= SEARCH =================
        search_frame = tk.Frame(self, bg="#b2e5ed")
        search_frame.pack(fill="x", padx=15, pady=5)

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 13),
            width=35,
            fg="gray"
        )
        self.search_entry.insert(0, "e.g. student name or fetcher name")
        self.search_entry.pack(side="right", padx=5)

        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<FocusOut>", self.add_placeholder)

        tk.Button(search_frame, text="Search", command=self.search).pack(side="right")

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

        self.create_form(forms, "FETCHER INFORMATION",
            [("Fetcher RFID", self.rfid_var),
             ("Name", self.name_var),
             ("Address", self.address_var),
             ("Contact", self.contact_var),
             ("Paired RFID", self.paired_rfid_var)], 0)

        self.create_form(forms, "STUDENT INFORMATION",
            [("Student RFID", self.student_rfid_var),
             ("Student ID", self.student_id_var),
             ("Name", self.student_name_var),
             ("Grade", self.grade_var),
             ("Teacher", self.teacher_var)], 1)

        # ================= BUTTONS =================
        btn_frame = tk.Frame(self, bg="#b2e5ed")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="ADD", bg="#4CAF50", fg="white",
                  font=("Arial", 12, "bold"), width=12,
                  command=self.add_record).pack(side="left", padx=5)

        tk.Button(btn_frame, text="EDIT", bg="#2196F3", fg="white",
                  font=("Arial", 12, "bold"), width=12,
                  command=self.edit_record).pack(side="left", padx=5)

        tk.Button(btn_frame, text="DELETE", bg="#F44336", fg="white",
                  font=("Arial", 12, "bold"), width=12,
                  command=self.delete_record).pack(side="left", padx=5)

        # ================= TABLE =================
        table_frame = tk.Frame(self, bg="white", bd=2, relief="groove")
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = (
            "registration_id", "rfid", "fetcher_name", "student_rfid",
            "address", "contact", "student_id", "student_name",
            "grade", "teacher", "paired_rfid"
        )

        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        self.table.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        scrollbar.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=scrollbar.set)

        for col in columns:
            self.table.heading(col, text=col.replace("_", " ").title())
            self.table.column(col, width=120, anchor="center")

        self.table.column("registration_id", width=0, stretch=False)
        self.table.bind("<<TreeviewSelect>>", self.load_selected)

        # ================= PAGINATION =================
        pagination = tk.Frame(self, bg="#b2e5ed")
        pagination.pack(pady=5)

        tk.Button(pagination, text="◀ Previous", command=self.prev_page).pack(side="left", padx=5)
        self.page_label = tk.Label(pagination, text="Page 1 of 1",
                                   bg="#b2e5ed", font=("Arial", 11, "bold"))
        self.page_label.pack(side="left", padx=10)
        tk.Button(pagination, text="Next ▶", command=self.next_page).pack(side="left", padx=5)

        self.load_data()

    # ================= SEARCH PLACEHOLDER =================
    def clear_placeholder(self, _):
        if self.search_entry.get().startswith("e.g"):
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="black")

    def add_placeholder(self, _):
        if not self.search_entry.get():
            self.search_entry.insert(0, "e.g. student name or fetcher name")
            self.search_entry.config(fg="gray")

    # ================= FORM CREATOR =================
    def create_form(self, parent, title, fields, col):
        frame = tk.Frame(parent, bg="white", bd=2, relief="groove", padx=10, pady=5)
        frame.grid(row=0, column=col, padx=10, pady=5, sticky="n")
        tk.Label(frame, text=title, font=("Arial", 16, "bold"),
                 bg="white", fg="#0047AB").pack(pady=5)

        for label, var in fields:
            row = tk.Frame(frame, bg="white")
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label + ":", bg="white",
                     width=14, anchor="w").pack(side="left")
            tk.Entry(row, textvariable=var, font=("Arial", 12))\
                .pack(side="right", fill="x", expand=True)

    # ================= DATABASE + PAGINATION =================
    def load_data(self):
        self.is_searching = False
        self.current_page = 1
        self._load_paginated_data()

    def _load_paginated_data(self, where="", params=()):
        self.table.delete(*self.table.get_children())
        offset = (self.current_page - 1) * self.page_size

        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM registrations {where}", params)
                self.total_records = cursor.fetchone()[0]
                self.total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)

                cursor.execute(f"""
                    SELECT registration_id, rfid, fetcher_name, student_rfid,
                           address, contact, student_id, student_name,
                           grade, teacher, paired_rfid
                    FROM registrations
                    {where}
                    ORDER BY registration_id DESC
                    LIMIT %s OFFSET %s
                """, params + (self.page_size, offset))

                for row in cursor.fetchall():
                    self.table.insert("", "end", values=row)

        self.page_label.config(text=f"Page {self.current_page} of {self.total_pages}")

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.reload_page()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.reload_page()

    def reload_page(self):
        self.search() if self.is_searching else self._load_paginated_data()

    # ================= SEARCH =================
    def search(self):
        if self.search_var.get().startswith("e.g") or not self.search_var.get().strip():
            messagebox.showwarning("Search", "Please enter a keyword to search.")
            return

        self.is_searching = True
        self.current_page = 1
        key = "%" + self.search_var.get() + "%"

        where = """
            WHERE rfid LIKE %s OR fetcher_name LIKE %s
               OR student_name LIKE %s OR student_id LIKE %s
               OR grade LIKE %s OR teacher LIKE %s
               OR paired_rfid LIKE %s
        """
        params = (key, key, key, key, key, key, key)
        self._load_paginated_data(where, params)

    # ================= CRUD WITH VALIDATION =================
    def add_record(self):
        if not all([
            self.rfid_var.get(),
            self.name_var.get(),
            self.student_rfid_var.get(),
            self.student_name_var.get()
        ]):
            messagebox.showwarning("Missing Information",
                                   "Please fill in all required fields.")
            return

        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO registrations
                    (rfid, fetcher_name, student_rfid, address, contact,
                     student_id, student_name, grade, teacher, paired_rfid)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    self.rfid_var.get(), self.name_var.get(),
                    self.student_rfid_var.get(), self.address_var.get(),
                    self.contact_var.get(), self.student_id_var.get(),
                    self.student_name_var.get(), self.grade_var.get(),
                    self.teacher_var.get(), self.paired_rfid_var.get()
                ))
                conn.commit()

        messagebox.showinfo("Success", "Record added successfully.")
        self.clear_form()
        self.load_data()

    def edit_record(self):
        if not self.selected_registration_id:
            messagebox.showwarning("Edit", "Please select a record to edit.")
            return

        if not all([
            self.rfid_var.get(),
            self.name_var.get(),
            self.student_rfid_var.get(),
            self.student_name_var.get()
        ]):
            messagebox.showwarning(
                "Missing Information",
                "Please fill in all required fields."
            )
            return

        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE registrations SET
                        rfid=%s,
                        fetcher_name=%s,
                        student_rfid=%s,
                        address=%s,
                        contact=%s,
                        student_id=%s,
                        student_name=%s,
                        grade=%s,
                        teacher=%s,
                        paired_rfid=%s
                    WHERE registration_id=%s
                """, (
                    self.rfid_var.get(),
                    self.name_var.get(),
                    self.student_rfid_var.get(),
                    self.address_var.get(),
                    self.contact_var.get(),
                    self.student_id_var.get(),
                    self.student_name_var.get(),
                    self.grade_var.get(),
                    self.teacher_var.get(),
                    self.paired_rfid_var.get(),
                    self.selected_registration_id
                ))
                conn.commit()

        messagebox.showinfo("Updated", "Record updated successfully.")
        self.clear_form()
        self.load_data()

    def delete_record(self):
        if not self.selected_registration_id:
            messagebox.showwarning("Delete", "Please select a record to delete.")
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to permanently delete this record?"
        ):
            return

        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM registrations WHERE registration_id=%s",
                    (self.selected_registration_id,)
                )
                conn.commit()

        messagebox.showinfo("Deleted", "Record deleted successfully.")
        self.clear_form()
        self.load_data()

    # ================= UTIL =================
    def load_selected(self, _):
        data = self.table.item(self.table.focus(), "values")
        if not data:
            return

        self.selected_registration_id = data[0]
        self.rfid_var.set(data[1])
        self.name_var.set(data[2])
        self.student_rfid_var.set(data[3])
        self.address_var.set(data[4])
        self.contact_var.set(data[5])
        self.student_id_var.set(data[6])
        self.student_name_var.set(data[7])
        self.grade_var.set(data[8])
        self.teacher_var.set(data[9])
        self.paired_rfid_var.set(data[10])

    def check_duplicate_rfid(self, uid):
        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM registrations WHERE rfid=%s OR student_rfid=%s",
                    (uid, uid)
                )
                return cursor.fetchone() is not None

    def clear_form(self):
        self.rfid_var.set("")
        self.name_var.set("")
        self.address_var.set("")
        self.contact_var.set("")
        self.paired_rfid_var.set("")
        self.student_rfid_var.set("")
        self.student_id_var.set("")
        self.student_name_var.set("")
        self.grade_var.set("")
        self.teacher_var.set("")
        self.selected_registration_id = None

    # ================= SERIAL READING =================
    def read_serial(self):
        while self.ser and self.ser.is_open:
            try:
                uid = self.ser.readline().decode(errors="ignore").strip()
                if uid:
                    print("RFID scanned:", uid)  # You can add auto-fill here if needed
            except Exception:
                break
