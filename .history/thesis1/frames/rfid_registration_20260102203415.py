import tkinter as tk
from tkinter import messagebox, ttk
import sys, os
import serial, threading, time

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

        # ================= SCAN STAGE =================
        self.scan_stage = "fetcher"   # fetcher → student

        # ================= SERIAL RFID =================
        try:
            self.ser = serial.Serial("COM3", 9600, timeout=1)
            time.sleep(2)
            threading.Thread(target=self.read_serial, daemon=True).start()
        except Exception as e:
            messagebox.showwarning("RFID", f"RFID reader not detected:\n{e}")
            self.ser = None

        # ================= SEARCH BAR =================
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self, textvariable=self.search_var,
                                     font=("Arial", 15), width=30, fg="gray")
        self.search_entry.place(x=450, y=20)
        self.search_entry.insert(0, "Search")
        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<FocusOut>", self.add_placeholder)

        tk.Button(self, text="🔍", command=self.search).place(x=780, y=20)

        # ================= VARIABLES =================
        self.rfid_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.contact_var = tk.StringVar()
        self.paired_rfid_var = tk.StringVar()

        self.student_id_var = tk.StringVar()
        self.student_name_var = tk.StringVar()
        self.grade_var = tk.StringVar()
        self.teacher_var = tk.StringVar()

        # ================= FETCHER FRAME =================
        self.fetcher_frame = tk.Frame(self, bg="white", bd=2, relief="groove", width=500, height=330)
        self.fetcher_frame.place(x=80, y=80)
        self.fetcher_frame.pack_propagate(False)

        tk.Label(self.fetcher_frame, text="FETCHER INFORMATION",
                 font=("Arial", 22, "bold"), bg="white", fg="#0047AB").pack(pady=10)

        fetcher_fields = [
            ("FETCHER RFID:", self.rfid_var),
            ("Name:", self.name_var),
            ("Address:", self.address_var),
            ("Contact:", self.contact_var),
            ("Paired RFID:", self.paired_rfid_var),
        ]

        y = 60
        for label, var in fetcher_fields:
            tk.Label(self.fetcher_frame, text=label, bg="white",
                     font=("Arial", 13)).place(x=20, y=y)
            tk.Entry(self.fetcher_frame, textvariable=var,
                     font=("Arial", 13), width=30).place(x=200, y=y)
            y += 45

        # ================= STUDENT FRAME =================
        self.student_frame = tk.Frame(self, bg="white", bd=2, relief="groove", width=500, height=330)
        self.student_frame.place(x=760, y=80)
        self.student_frame.pack_propagate(False)

        tk.Label(self.student_frame, text="STUDENT INFORMATION",
                 font=("Arial", 22, "bold"), bg="white", fg="#0047AB").pack(pady=10)

        student_fields = [
            ("Student RFID:", self.student_id_var),
            ("Student ID:", self.studen_id_var),
            ("Name:", self.student_name_var),
            ("Grade:", self.grade_var),
            ("Teacher:", self.teacher_var),
        ]

        y = 60
        for label, var in student_fields:
            tk.Label(self.student_frame, text=label, bg="white",
                     font=("Arial", 13)).place(x=20, y=y)
            tk.Entry(self.student_frame, textvariable=var,
                     font=("Arial", 13), width=30).place(x=200, y=y)
            y += 45

        # ================= BUTTONS =================
        tk.Button(self, text="ADD", bg="#4CAF50", fg="white",
                  font=("Arial", 14, "bold"), width=12,
                  command=self.add_record).place(x=455, y=430)

        tk.Button(self, text="EDIT", bg="#2196F3", fg="white",
                  font=("Arial", 14, "bold"), width=12,
                  command=self.edit_record).place(x=605, y=430)

        tk.Button(self, text="DELETE", bg="#F44336", fg="white",
                  font=("Arial", 14, "bold"), width=12,
                  command=self.delete_record).place(x=755, y=430)

        # ================= TABLE =================
        columns = ("RFID", "Fetcher Name", "Address", "Contact",
                   "Student ID", "Student Name", "Grade Level", "Teacher", "paired_rfid")

        self.table = ttk.Treeview(self, columns=columns, show="headings", height=7)
        self.table.place(x=100, y=500, width=1150)

        for col in columns:
            self.table.heading(col, text=col.replace("_", " ").title())
            self.table.column(col, width=120, anchor="center")

        self.table.bind("<<TreeviewSelect>>", self.load_selected)

        self.load_data()

    # ================= SERIAL READ =================
    def read_serial(self):
        while self.ser and self.ser.is_open:
            line = self.ser.readline().decode(errors="ignore").strip()
            if not line:
                continue

            # Remove "Reader1:" or any label
            if ":" in line:
                uid = line.split(":")[-1].strip()
            else:
                uid = line.strip()

            self.root.after(0, self.process_uid, uid)

    def process_uid(self, uid):
        # FIRST TAP → FETCHER
        if self.scan_stage == "fetcher":
            if self.check_duplicate_rfid(uid):
                messagebox.showerror("Duplicate", "Fetcher RFID already exists")
                return

            self.rfid_var.set(uid)
            self.scan_stage = "student"
            messagebox.showinfo("Next", "Fetcher scanned.\nNow tap STUDENT RFID.")

        # SECOND TAP → STUDENT
        elif self.scan_stage == "student":
            self.student_id_var.set(uid)
            self.paired_rfid_var.set(uid)
            self.scan_stage = "fetcher"
            messagebox.showinfo("Ready", "Student scanned.\nYou may now ADD the record.")

    # ================= DATABASE =================
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

    def add_record(self):
        if not self.rfid_var.get() or not self.student_id_var.get():
            messagebox.showwarning("Missing", "Scan both Fetcher and Student RFID")
            return

        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO registrations
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                self.rfid_var.get(), self.name_var.get(),self.student_rfid_var.get(),
                self.address_var.get(), self.contact_var.get(),
                self.student_id_var.get(), self.student_name_var.get(),
                self.grade_var.get(), self.teacher_var.get(),
                self.paired_rfid_var.get()
            ))
            conn.commit()
            messagebox.showinfo("Success", "Record added")
            self.load_data()
            self.clear_fields()
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def edit_record(self):
        if not self.rfid_var.get():
            return
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE registrations SET
                fetcher_name=%s, address=%s, contact=%s,
                student_id=%s, student_name=%s,
                grade=%s, teacher=%s, paired_rfid=%s, student_r
                WHERE rfid=%s
            """, (
                self.name_var.get(), self.address_var.get(),
                self.contact_var.get(), self.student_id_var.get(),
                self.student_name_var.get(), self.grade_var.get(),
                self.teacher_var.get(), self.paired_rfid_var.get(),
                self.rfid_var.get()
            ))
            conn.commit()
            messagebox.showinfo("Updated", "Record updated")
            self.load_data()
            self.clear_fields()
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def delete_record(self):
        if not self.rfid_var.get():
            return
        if not messagebox.askyesno("Confirm", "Delete record?"):
            return

        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM registrations WHERE rfid=%s",
                           (self.rfid_var.get(),))
            conn.commit()
            messagebox.showinfo("Deleted", "Record deleted")
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
         self.address_var.set(data[2]), self.contact_var.set(data[3]),
         self.student_id_var.set(data[4]), self.student_name_var.set(data[5]),
         self.grade_var.set(data[6]), self.teacher_var.set(data[7]),
         self.paired_rfid_var.set(data[8]))

    def clear_fields(self):
        for v in (self.rfid_var, self.name_var, self.address_var,
                  self.contact_var, self.student_id_var,
                  self.student_name_var, self.grade_var,
                  self.teacher_var, self.paired_rfid_var):
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
        keyword = "%" + self.search_var.get() + "%"
        self.table.delete(*self.table.get_children())
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM registrations
                WHERE rfid LIKE %s OR fetcher_name LIKE %s
                   OR student_name LIKE %s OR paired_rfid LIKE %s
            """, (keyword, keyword, keyword, keyword))
            for row in cursor.fetchall():
                self.table.insert("", "end", values=row)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    RfidRegistration(root)
    root.mainloop()
