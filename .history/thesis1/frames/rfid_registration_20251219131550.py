import tkinter as tk
from tkinter import messagebox, ttk

import sys
import os

# Add the parent directory of 'frames' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.database import db_connect


class RfidRegistration(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg="#b2e5ed")
        self.root = root
        root.title("RFID MANAGEMENT SYSTEM - RFID REGISTRATION")
        root.geometry("1350x700+0+0")
        self.pack(fill="both", expand=True)
        

        #headding 

        self.title = tk.Label(self, height=95, bg="#0047AB", bd=2, relief="groove")
        self.title.pack(fill = "x")

        tk.Label(
            self.title,
            text="RFID REGISTRATION",
            font=("Arial", 24, "bold"),
            bg="#0047AB",
            fg="white"
        ).place(x=50, y=25)

        # ================= FETCHER FRAME =================
        self.fetcher_frame = tk.Frame(self, width=450, height=350, bg="white", bd=2, relief="groove")
        self.fetcher_frame.place(x=60, y=90)
        self.fetcher_frame.pack_propagate(False)
        tk.Label(self.fetcher_frame, text="FETCHER INFORMATION",
                 font=("Arial", 24, "bold"), bg="white", fg="#0047AB").place(x=20, y=20)

        # Fetcher fields

        self.photo_frame = tk.Frame(
            self.student_left, width=200, height=200,
            bg="#E0E0E0", bd=2, relief="ridge"
        )
        self.photo_frame.place(x=20, y=20)
        self.photo_frame.pack_propagate(False)

        self.photo_label = tk.Label(self.photo_frame, bg="#E0E0E0")
        self.photo_label.pack(fill="both", expand=True)

        tk.Button(
            self.fetcher_frame,
            text="Upload Photo",
            width=15,
            command=self.upload_photo
        ).place(x=60, y=240)

        tk.Label(self.fetcher_frame, text="RFID:", font=("Arial", 14), bg="white").place(x=20, y=80)
        self.rfid_var = tk.StringVar()
        tk.Entry(self.fetcher_frame, textvariable=self.rfid_var, font=("Arial", 14), width=30).place(x=90, y=80)

        tk.Label(self.fetcher_frame, text="Name:", font=("Arial", 14), bg="white").place(x=20, y=120)
        self.name_var = tk.StringVar()
        tk.Entry(self.fetcher_frame, textvariable=self.name_var, font=("Arial", 14), width=30).place(x=90, y=120)

        tk.Label(self.fetcher_frame, text="Address:", font=("Arial", 14), bg="white").place(x=20, y=160)
        self.address_var = tk.StringVar()
        tk.Entry(self.fetcher_frame, textvariable=self.address_var, font=("Arial", 14), width=30).place(x=140, y=160)

        tk.Label(self.fetcher_frame, text="Contact:", font=("Arial", 14), bg="white").place(x=20, y=200)
        self.contact_var = tk.StringVar()
        tk.Entry(self.fetcher_frame, textvariable=self.contact_var, font=("Arial", 14), width=30).place(x=100, y=200)

        # ================= STUDENT FRAME =================
        self.student_frame = tk.Frame(self, width=450, height=350, bg="white", bd=2, relief="groove")
        self.student_frame.place(x=850, y=90)
        self.student_frame.pack_propagate(False)
        tk.Label(self.student_frame, text="STUDENT INFORMATION",
                 font=("Arial", 24, "bold"), bg="white", fg="#0047AB").place(x=20, y=20)

        tk.Label(self.student_frame, text="Student ID:", font=("Arial", 14), bg="white").place(x=20, y=80)
        self.student_id_var = tk.StringVar()
        tk.Entry(self.student_frame, textvariable=self.student_id_var, font=("Arial", 14), width=30).place(x=160, y=80)

        tk.Label(self.student_frame, text="Name:", font=("Arial", 14), bg="white").place(x=20, y=120)
        self.student_name_var = tk.StringVar()
        tk.Entry(self.student_frame, textvariable=self.student_name_var, font=("Arial", 14), width=30).place(x=160, y=120)

        tk.Label(self.student_frame, text="Grade:", font=("Arial", 14), bg="white").place(x=20, y=160)
        self.grade_var = tk.StringVar()
        tk.Entry(self.student_frame, textvariable=self.grade_var, font=("Arial", 14), width=30).place(x=160, y=160)

        tk.Label(self.student_frame, text="Teacher:", font=("Arial", 14), bg="white").place(x=20, y=200)
        self.teacher_var = tk.StringVar()
        tk.Entry(self.student_frame, textvariable=self.teacher_var, font=("Arial", 14), width=30).place(x=160, y=200)

        # ================= BUTTONS =================
        btn_y = 470
        tk.Button(self, text="ADD", width=12, font=("Arial", 14, "bold"),
                  bg="#4CAF50", fg="white", command=self.add_record).place(x=480, y=btn_y)
        tk.Button(self, text="EDIT", width=12, font=("Arial", 14, "bold"),
                  bg="#2196F3", fg="white", command=self.edit_record).place(x=630, y=btn_y)
        tk.Button(self, text="DELETE", width=12, font=("Arial", 14, "bold"),
                  bg="#F44336", fg="white", command=self.delete_record).place(x=780, y=btn_y)

        # ================= TABLE =================
        columns = ("rfid", "fetcher_name", "student_id", "student_name", "grade", "teacher")
        self.table = ttk.Treeview(self, columns=columns, show="headings", height=6)
        self.table.place(x=200, y=540, width=1200)
        for col in columns:
            self.table.heading(col, text=col.replace("_", " ").title())
            self.table.column(col, width=150)
        self.table.bind("<<TreeviewSelect>>", self.load_selected)

        # Load table initially
        self.load_data()

    # ================= DATABASE FUNCTIONS =================
    def load_data(self):
        self.table.delete(*self.table.get_children())
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT rfid, fetcher_name, student_id, student_name, grade, teacher FROM registrations")
            rows = cursor.fetchall()
            for row in rows:
                self.table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def add_record(self):
        try:
            conn = db_connect()
            cursor = conn.cursor()
            sql = """
            INSERT INTO registrations
            (rfid, fetcher_name, address, contact, student_id, student_name, grade, teacher)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """
            values = (
                self.rfid_var.get(), self.name_var.get(), self.address_var.get(),
                self.contact_var.get(), self.student_id_var.get(), self.student_name_var.get(),
                self.grade_var.get(), self.teacher_var.get()
            )
            cursor.execute(sql, values)
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
        item = self.table.focus()
        if not item:
            messagebox.showwarning("Select", "Select a record first")
            return
        try:
            conn = db_connect()
            cursor = conn.cursor()
            sql = """
            UPDATE registrations SET
            fetcher_name=%s, address=%s, contact=%s,
            student_id=%s, student_name=%s, grade=%s, teacher=%s
            WHERE rfid=%s
            """
            values = (
                self.name_var.get(), self.address_var.get(), self.contact_var.get(),
                self.student_id_var.get(), self.student_name_var.get(),
                self.grade_var.get(), self.teacher_var.get(), self.rfid_var.get()
            )
            cursor.execute(sql, values)
            conn.commit()
            self.load_data()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def delete_record(self):
        if not self.rfid_var.get():
            messagebox.showwarning("Select", "Select a record")
            return
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM registrations WHERE rfid=%s", (self.rfid_var.get(),))
            conn.commit()
            self.load_data()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            cursor.close()
            conn.close()

    # ================= TREEVIEW & FIELDS =================
    def load_selected(self, event):
        item = self.table.focus()
        if not item:
            return
        data = self.table.item(item, "values")
        self.rfid_var.set(data[0])
        self.name_var.set(data[1])
        self.student_id_var.set(data[2])
        self.student_name_var.set(data[3])
        self.grade_var.set(data[4])
        self.teacher_var.set(data[5])

    def clear_fields(self):
        for var in (self.rfid_var, self.name_var, self.address_var, self.contact_var,
                    self.student_id_var, self.student_name_var, self.grade_var, self.teacher_var):
            var.set("")

    # ================= SEARCH BAR =================
    def clear_placeholder(self, event):
        if self.search_entry.get() == "Search":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="black")

    def add_placeholder(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search")
            self.search_entry.config(fg="gray")

    def search(self):
        keyword = self.search_var.get()
        self.table.delete(*self.table.get_children())
        try:
            conn = db_connect()
            cursor = conn.cursor()
            sql = """
            SELECT rfid, fetcher_name, student_id, student_name, grade, teacher
            FROM registrations
            WHERE rfid LIKE %s OR fetcher_name LIKE %s OR student_name LIKE %s
            """
            value = f"%{keyword}%"
            cursor.execute(sql, (value, value, value))
            for row in cursor.fetchall():
                self.table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = RfidRegistration(root)
    root.mainloop()
