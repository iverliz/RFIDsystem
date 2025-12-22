import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode



class RfidRegistration(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg="#b2e5ed")
        self.root = root
        root.title("RFID MANAGEMENT SYSTEM - RFID REGISTRATION")
        root.geometry("1350x700+0+0")
        self.pack(fill="both", expand=True)

        # ================= SEARCH BAR =================
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

        # ================= COMMON FRAME SETTINGS =================
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
        self.paired_rfid_var = tk.StringVar()

        fetcher_fields = [
            ("RFID:", self.rfid_var),
            ("Name:", self.name_var),
            ("Address:", self.address_var),
            ("Contact:", self.contact_var),
            ("Paired RFID (Student):", self.paired_rfid_var),
        ]

        y = 60
        for label, var in fetcher_fields:
            tk.Label(self.fetcher_frame, text=label, font=("Arial", 13), bg="white").place(x=20, y=y)
            tk.Entry(self.fetcher_frame, textvariable=var, font=("Arial", 13), width=30).place(x=200, y=y)
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

        student_fields = [
            ("Student ID:", self.student_id_var),
            ("Name:", self.student_name_var),
            ("Grade:", self.grade_var),
            ("Teacher:", self.teacher_var),
        ]

        y = 60
        for label, var in student_fields:
            tk.Label(self.student_frame, text=label, font=("Arial", 13), bg="white").place(x=20, y=y)
            tk.Entry(self.student_frame, textvariable=var, font=("Arial", 13), width=30).place(x=200, y=y)
            y += 45

        # ================= BUTTONS (CENTERED) =================
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

        # ================= TABLE (CENTERED BELOW) =================
        columns = (
            "rfid", "fetcher_name", "address", "contact",
            "student_id", "student_name", "grade", "teacher", "paired_rfid"
        )

        self.table = ttk.Treeview(self, columns=columns, show="headings", height=7)

        table_width = 1150
        self.table.place(
            x=(1350 - table_width) // 2,
            y=btn_y + 70,
            width=table_width
        )

        for col in columns:
            self.table.heading(col, text=col.replace("_", " ").title())
            self.table.column(col, width=120, anchor="center")

        self.table.bind("<<TreeviewSelect>>", self.load_selected)

        # ================= RFID CAPTURE =================
        self.rfid_buffer = ""
        self.root.bind("<Key>", self.capture_rfid)

        self.load_data()

    # ================= DATABASE =================
    def load_data(self):
        self.table.delete(*self.table.get_children())
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT rfid, fetcher_name, address, contact,
                       student_id, student_name, grade, teacher, paired_rfid
                FROM registrations
            """)
            for row in cursor.fetchall():
                self.table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def add_record(self):
        if not self.rfid_var.get():
            messagebox.showwarning("Missing RFID", "Scan or enter RFID first")
            return

        if self.check_duplicate_rfid(self.rfid_var.get()):
            messagebox.showwarning("Duplicate RFID", "This RFID is already registered")
            return

        conn = cursor = None
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
            self.load_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Record added successfully")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def edit_record(self):
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE registrations SET
                fetcher_name=%s, address=%s, contact=%s,
                student_id=%s, student_name=%s,
                grade=%s, teacher=%s, paired_rfid=%s
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
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def delete_record(self):
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM registrations WHERE rfid=%s",
                (self.rfid_var.get(),)
            )
            conn.commit()
            self.load_data()
            self.clear_fields()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # ================= SELECT AND SEARCH =================
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
            self.paired_rfid_var.set(data[8]),
        )

    def search(self):
        keyword = f"%{self.search_var.get()}%"
        self.table.delete(*self.table.get_children())
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT rfid, fetcher_name, address, contact,
                       student_id, student_name, grade, teacher, paired_rfid
                FROM registrations
                WHERE rfid LIKE %s OR fetcher_name LIKE %s
                   OR student_name LIKE %s OR paired_rfid LIKE %s
            """, (keyword, keyword, keyword, keyword))
            for row in cursor.fetchall():
                self.table.insert("", "end", values=row)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def clear_fields(self):
        for var in (
            self.rfid_var, self.name_var, self.address_var, self.contact_var,
            self.student_id_var, self.student_name_var,
            self.grade_var, self.teacher_var, self.paired_rfid_var
        ):
            var.set("")

    def clear_placeholder(self, _):
        if self.search_entry.get() == "Search":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="black")

    def add_placeholder(self, _):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search")
            self.search_entry.config(fg="gray")

    # ================= RFID HANDLING =================
    def capture_rfid(self, event):
        if event.keysym == "Return":  # RFID finished
            uid = self.rfid_buffer.strip()
            self.rfid_buffer = ""
            if uid:
                self.rfid_var.set(uid)
                self.match_rfid(uid)
        else:
            if event.char.isalnum():
                self.rfid_buffer += event.char

    def match_rfid(self, uid):
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT rfid, fetcher_name, address, contact,
                       student_id, student_name, grade, teacher, paired_rfid
                FROM registrations
                WHERE rfid=%s OR paired_rfid=%s
            """, (uid, uid))
            row = cursor.fetchone()
            if row:
                (
                    rfid, fetcher_name, address, contact,
                    student_id, student_name, grade, teacher, paired_rfid
                ) = row

                self.rfid_var.set(rfid)
                self.name_var.set(fetcher_name)
                self.address_var.set(address)
                self.contact_var.set(contact)
                self.student_id_var.set(student_id)
                self.student_name_var.set(student_name)
                self.grade_var.set(grade)
                self.teacher_var.set(teacher)
                self.paired_rfid_var.set(paired_rfid)

                # Highlight in table
                for item in self.table.get_children():
                    if self.table.item(item, "values")[0] == uid:
                        self.table.selection_set(item)
                        self.table.see(item)
                        break

                messagebox.showinfo("RFID Found", "Record loaded successfully")
            else:
                messagebox.showinfo(
                    "New RFID",
                    "RFID not found.\nYou can now register this card."
                )
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def check_duplicate_rfid(self, uid):
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT rfid FROM registrations WHERE rfid=%s OR paired_rfid=%s", (uid, uid))
            return cursor.fetchone() is not None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


