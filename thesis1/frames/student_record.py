import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import ImageTk, Image
import os
import sys
import time
import io 

# ================= PATH SETUP =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.database import db_connect

# ================= LOOKUP DIALOG CLASS =================
class LookupDialog(tk.Toplevel):
    def __init__(self, parent, title, table, search_col, display_cols):
        super().__init__(parent)
        self.title(f"Link {title}")
        self.geometry("500x400")
        self.grab_set() # Make window modal
        self.result = None
        self.table = table
        self.search_col = search_col
        self.display_cols = display_cols

        tk.Label(self, text=f"Search {title}:", font=("Arial", 10, "bold")).pack(pady=10)
        self.search_var = tk.StringVar()
        entry = tk.Entry(self, textvariable=self.search_var, width=40)
        entry.pack(pady=5)
        entry.bind("<KeyRelease>", lambda e: self.search())

        self.tree = ttk.Treeview(self, columns=display_cols, show="headings", height=10)
        for col in display_cols:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=120)
        self.tree.pack(pady=10, padx=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Select & Link", bg="#4CAF50", fg="white", 
                  command=self.on_select, width=15).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.destroy, width=15).grid(row=0, column=1, padx=5)
        self.search() # Initial load

    def search(self):
        query_str = self.search_var.get().strip()
        self.tree.delete(*self.tree.get_children())
        try:
            with db_connect() as conn:
                with conn.cursor(dictionary=True) as cur:
                    sql = f"SELECT {', '.join(self.display_cols)} FROM {self.table} WHERE {self.search_col} LIKE %s"
                    cur.execute(sql, (f"%{query_str}%",))
                    for row in cur.fetchall():
                        values = [row[col] for col in self.display_cols]
                        self.tree.insert("", "end", values=values)
        except Exception as e:
            print(f"Lookup Error: {e}")

    def on_select(self):
        selected = self.tree.selection()
        if selected:
            self.result = self.tree.item(selected[0], "values")
            self.destroy()

# ================= MAIN CLASS =================
class StudentRecord(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#b2e5ed")
        self.controller = controller
        self.photo_path = None

        # ================= PAGINATION & SEARCH STATE =================
        self.page_size = 100
        self.current_page = 1
        self.total_students = 0
        self.search_results = [] 
        self.search_page = 1     

        # ================= VALIDATORS =================
        self.num_validate = self.register(self.only_numbers)
        self.contact_validate = self.register(self.contact_limit)

        # ================= HEADER =================
        header = tk.Frame(self, height=70, bg="#0047AB")
        header.pack(fill="x")

        tk.Label(header, text="STUDENT INFORMATION", font=("Arial", 20, "bold"),
                 bg="#0047AB", fg="white").place(x=30, y=18)

        # ================= LEFT PANEL =================
        self.left_box = tk.Frame(self, width=480, height=520, bg="white", bd=2, relief="groove")
        self.left_box.place(x=20, y=90)
        self.left_box.pack_propagate(False)

        # ================= PHOTO =================
        self.photo_frame = tk.Frame(self.left_box, width=160, height=160, bg="#E0E0E0", bd=2, relief="ridge")
        self.photo_frame.place(x=20, y=20)
        self.photo_frame.pack_propagate(False)

        self.photo_label = tk.Label(self.photo_frame, bg="#E0E0E0")
        self.photo_label.pack(fill="both", expand=True)

        self.upload_btn = tk.Button(self.left_box, text="Upload Photo", width=14, command=self.upload_photo)
        self.upload_btn.place(x=210, y=80)
        
        self.remove_photo_btn = tk.Button(self.left_box, text="Remove Photo", width=14, fg="red", command=self.remove_photo)
        self.remove_photo_btn.place(x=210, y=115) 

        # ================= VARIABLES =================
        self.student_name_var = tk.StringVar()
        self.grade_var = tk.StringVar()
        self.student_id_var = tk.StringVar()
        self.guardian_name_var = tk.StringVar()
        self.guardian_contact_var = tk.StringVar()
        self.teacher_name_var = tk.StringVar()
        self.fetcher_code_var = tk.StringVar() # Important: To link the ID
        
        self.guardian_contact_var.trace_add("write", self.format_contact)

        self.edit_mode = False
        self.original_student_id = None

        self.edit_label = tk.Label(self.left_box, text="VIEW MODE", font=("Arial", 10, "bold"),
                                   fg="gray", bg="white")
        self.edit_label.place(x=280, y=10)

        # ================= FORM =================
        fields = [
            ("Full Name:", self.student_name_var),
            ("Grade:", self.grade_var),
            ("Student ID:", self.student_id_var),
            ("Guardian Name:", self.guardian_name_var),
            ("Guardian Contact:", self.guardian_contact_var),
            ("Teacher Name:", self.teacher_name_var),
        ]

        self.entries = {}
        y = 200
        for i, (label, var) in enumerate(fields):
            tk.Label(self.left_box, text=label, bg="white", font=("Arial", 11)).place(x=20, y=y + i * 40)

            if label == "Grade:":
                entry = ttk.Spinbox(self.left_box, from_=1, to=12, textvariable=var, width=28, state="readonly")
            elif label == "Student ID:":
                entry = tk.Entry(self.left_box, textvariable=var, width=30, font=("Arial", 11),
                                 validate="key", validatecommand=(self.num_validate, "%P"))
                self.student_id_entry = entry
            elif label == "Guardian Contact:":
                entry = tk.Entry(self.left_box, textvariable=var, width=30, font=("Arial", 11),
                                 validate="key", validatecommand=(self.contact_validate, "%P"))
            else:
                entry = tk.Entry(self.left_box, textvariable=var, width=30, font=("Arial", 11))

            entry.place(x=150, y=y + i * 40)
            self.entries[label] = entry

            # Add Link Buttons
            if label == "Guardian Name:":
                tk.Button(self.left_box, text="🔗 Link", command=self.link_fetcher, bg="#eee", font=("Arial", 8)).place(x=400, y=y + i * 40)
            if label == "Teacher Name:":
                tk.Button(self.left_box, text="🔗 Link", command=self.link_teacher, bg="#eee", font=("Arial", 8)).place(x=400, y=y + i * 40)

        # ================= BUTTONS =================
        btn_frame = tk.Frame(self.left_box, bg="white")
        btn_frame.place(x=15, y=470)

        self.add_btn = tk.Button(btn_frame, text="ADD", width=9, bg="#4CAF50", fg="white",
                                 font=("Arial", 9, "bold"), command=self.add_student)
        self.add_btn.grid(row=0, column=0, padx=2)

        self.edit_btn = tk.Button(btn_frame, text="EDIT", width=9, bg="#2196F3", fg="white",
                                  font=("Arial", 9, "bold"), command=self.enable_edit_mode)
        self.edit_btn.grid(row=0, column=1, padx=2)

        self.update_btn = tk.Button(btn_frame, text="UPDATE", width=9, bg="#FF9800", fg="white",
                                    font=("Arial", 9, "bold"), command=self.edit_student, state="disabled")
        self.update_btn.grid(row=0, column=2, padx=2)

        self.delete_btn = tk.Button(btn_frame, text="DELETE", width=9, bg="#F44336", fg="white",
                                    font=("Arial", 9, "bold"), command=self.delete_student)
        self.delete_btn.grid(row=0, column=3, padx=2)

        # ================= RIGHT PANEL =================
        self.right_panel = tk.Frame(self, width=540, height=520, bg="white", bd=2, relief="groove")
        self.right_panel.place(x=520, y=90)
        self.right_panel.pack_propagate(False)

        tk.Label(self.right_panel, text="Search Student (Name/Grade/Student ID)", font=("Arial", 14, "bold"), bg="white").place(x=20, y=15)

        self.search_var = tk.StringVar()
        tk.Entry(self.right_panel, textvariable=self.search_var, width=25, font=("Arial", 11)).place(x=20, y=50)

        tk.Button(self.right_panel, text="Search", command=self.search_student).place(x=260, y=47)
        tk.Button(self.right_panel, text="Clear", command=self.clear_search).place(x=320, y=47)

        self.count_var = tk.StringVar()
        tk.Label(self.right_panel, textvariable=self.count_var, font=("Arial", 11, "bold"),
                 fg="#0047AB", bg="white").place(x=20, y=85)

        self.student_table = ttk.Treeview(self.right_panel, columns=("Student_id", "Student_name", "grade_lvl"),
                                          show="headings", height=15, takefocus=False)

        for col, txt, w in [("Student_id", "Student ID", 120), ("Student_name", "Full Name", 250), ("grade_lvl", "Grade", 100) ]:
            self.student_table.heading(col, text=txt)
            self.student_table.column(col, width=w)

        self.student_table.place(x=20, y=120, width=500)
        self.student_table.bind("<<TreeviewSelect>>", self.on_table_select)

        # Pagination Buttons
        nav = tk.Frame(self.right_panel, bg="white")
        nav.place(x=200, y=470)
        tk.Button(nav, text="◀ Prev", command=self.prev_page).grid(row=0, column=0, padx=5)
        tk.Button(nav, text="Next ▶", command=self.next_page).grid(row=0, column=1, padx=5)

        self.reset_ui_state()
        self.load_data()

    # ================= LINKING LOGIC =================
    def link_fetcher(self):
        # Searching the 'fetcher' table created in registration
        dialog = LookupDialog(self, "Fetcher", "fetcher", "fetcher_name", ["fetcher_name", "contact", "fetcher_code"])
        self.wait_window(dialog)
        if dialog.result:
            name, contact, code = dialog.result
            self.guardian_name_var.set(name)
            self.guardian_contact_var.set(contact)
            self.fetcher_code_var.set(code)

    def link_teacher(self):
        # Searching the 'registrations' table where teacher info might exist
        dialog = LookupDialog(self, "Adviser", "registrations", "teacher", ["teacher", "grade"])
        self.wait_window(dialog)
        if dialog.result:
            t_name, t_grade = dialog.result
            self.teacher_name_var.set(t_name)
            self.grade_var.set(t_grade)

    # ================= HELPERS & UI CONTROL =================
    def display_photo(self, data):
        try:
            if data:
                if isinstance(data, bytes):
                    stream = io.BytesIO(data)
                    img = Image.open(stream).resize((160, 160))
                else:
                    img = Image.open(data).resize((160, 160))
                self.photo = ImageTk.PhotoImage(img)
                self.photo_label.config(image=self.photo, text="")
                self.photo_label.image = self.photo
            else:
                self.photo_label.config(image="", text="NO PHOTO\nAVAILABLE", font=("Arial", 10, "bold"), fg="#666666")
                self.photo = None
        except Exception:
            self.photo_label.config(image="", text="Error Loading Image")
            
    def upload_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if path:
            self.photo_path = path
            self.display_photo(path)

    def remove_photo(self):
        self.photo_path = None
        self.display_photo(None)
    
    def only_numbers(self, v): return v.isdigit() or v == ""
    def contact_limit(self, v): return (v.isdigit() and len(v) <= 11) or v == ""

    def format_contact(self, *_):
        val = self.guardian_contact_var.get()
        if val.startswith("9") and len(val) == 10: self.guardian_contact_var.set("0" + val)

    def set_fields_state(self, state):
        for label, entry in self.entries.items():
            if label == "Grade:": entry.config(state="readonly" if state == "disabled" else "normal")
            else: entry.config(state=state)
        self.upload_btn.config(state=state)
        self.remove_photo_btn.config(state=state)

    def reset_ui_state(self):
        self.edit_mode = False
        self.original_student_id = None
        self.set_fields_state("disabled")
        self.student_id_entry.config(state="disabled")
        self.add_btn.config(text="ADD", state="normal", bg="#4CAF50")
        self.edit_btn.config(state="normal")
        self.delete_btn.config(text="DELETE", bg="#F44336")
        self.update_btn.config(state="disabled")
        self.edit_label.config(text="VIEW MODE", fg="gray", bg="white")
        self.clear_fields()

    def clear_fields(self):
        for var in (self.student_name_var, self.student_id_var, self.grade_var,
                    self.guardian_name_var, self.guardian_contact_var, self.teacher_name_var, self.fetcher_code_var):
            var.set("")
        self.display_photo(None)
        self.photo_path = None
        self.student_table.selection_remove(self.student_table.selection())

    # ================= DATA LOGIC =================
    def load_data(self):
        try:
            self.student_table.delete(*self.student_table.get_children())
            offset = (self.current_page - 1) * self.page_size
            with db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM student")
                    self.total_students = cursor.fetchone()[0]
                    cursor.execute("SELECT Student_id, Student_name, grade_lvl FROM student LIMIT %s OFFSET %s", 
                                   (self.page_size, offset))
                    for row in cursor.fetchall(): self.student_table.insert("", "end", values=row)

            total_p = max(1, (self.total_students + self.page_size - 1) // self.page_size)
            self.count_var.set(f"Students: {self.total_students} | Page {self.current_page}/{total_p}")
        except Exception as e: messagebox.showerror("Database Error", f"Could not load data: {e}")

    # (Previous Search/Pagination methods remain same...)
    def search_student(self):
        keyword = self.search_var.get().strip()
        if not keyword: return self.clear_search()
        try:
            with db_connect() as conn:
                with conn.cursor() as cursor:
                    query = "SELECT Student_id, Student_name, grade_lvl FROM student WHERE Student_name LIKE %s OR Student_id LIKE %s"
                    cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
                    self.search_results = cursor.fetchall()
            self.search_page = 1
            self.update_search_table()
        except Exception as e: messagebox.showerror("Search Error", str(e))

    def clear_search(self):
        self.search_var.set(""); self.search_results = []; self.current_page = 1 
        self.load_data(); self.reset_ui_state()

    def update_search_table(self):
        self.student_table.delete(*self.student_table.get_children())
        start = (self.search_page - 1) * self.page_size
        end = start + self.page_size
        for row in self.search_results[start:end]: self.student_table.insert("", "end", values=row)
        total_p = max(1, (len(self.search_results) + self.page_size - 1) // self.page_size)
        self.count_var.set(f"Matches: {len(self.search_results)} | Page {self.search_page}/{total_p}")

    def next_page(self):
        if self.search_var.get().strip():
            if self.search_page * self.page_size < len(self.search_results): self.search_page += 1; self.update_search_table()
        elif self.current_page * self.page_size < self.total_students: self.current_page += 1; self.load_data()

    def prev_page(self):
        if self.search_var.get().strip():
            if self.search_page > 1: self.search_page -= 1; self.update_search_table()
        elif self.current_page > 1: self.current_page -= 1; self.load_data()

    # ================= CRUD OPERATIONS =================
    def on_table_select(self, _):
        if self.edit_mode or self.add_btn["text"] == "SAVE": return
        sel = self.student_table.selection()
        if not sel: return
        student_id = self.student_table.item(sel[0], "values")[0]
        with db_connect() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM student WHERE Student_id=%s", (student_id,))
                student = cursor.fetchone()
        if student:
            self.student_id_var.set(student["Student_id"])
            self.student_name_var.set(student["Student_name"])
            self.grade_var.set(student["grade_lvl"])
            self.guardian_name_var.set(student["Guardian_name"])
            self.guardian_contact_var.set(student["Guardian_contact"])
            self.teacher_name_var.set(student["Teacher_name"])
            self.fetcher_code_var.set(student.get("fetcher_code", ""))
            self.photo_path = student["photo_path"]
            self.display_photo(self.photo_path)

    def add_student(self):
        if self.add_btn["text"] == "ADD":
            self.reset_ui_state(); self.set_fields_state("normal"); self.student_id_entry.config(state="normal")
            self.add_btn.config(text="SAVE", bg="#2E7D32"); self.edit_btn.config(state="disabled")
            self.delete_btn.config(text="CANCEL", bg="#757575"); return

        error = self.validate()
        if error: return messagebox.showerror("Error", error)
        
        sid = self.student_id_var.get()
        if self.student_id_exists(sid): return messagebox.showerror("Error", "Student ID already exists")

        binary_photo = None
        if self.photo_path and isinstance(self.photo_path, str) and os.path.exists(self.photo_path):
            img = Image.open(self.photo_path).convert("RGB")
            img_byte_arr = io.BytesIO(); img.save(img_byte_arr, format='JPEG')
            binary_photo = img_byte_arr.getvalue()

        try:
            with db_connect() as conn:
                with conn.cursor() as cursor:
                    query = """INSERT INTO student (Student_name, Student_id, grade_lvl, 
                               Guardian_name, Guardian_contact, Teacher_name, photo_path, fetcher_code)
                               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
                    cursor.execute(query, (
                        self.student_name_var.get(), sid, self.grade_var.get(), 
                        self.guardian_name_var.get(), self.guardian_contact_var.get(), 
                        self.teacher_name_var.get(), binary_photo, self.fetcher_code_var.get()
                    ))
                    conn.commit()
            messagebox.showinfo("Success", "Student added")
            self.reset_ui_state(); self.load_data()
        except Exception as e: messagebox.showerror("Error", str(e))

    def enable_edit_mode(self):
        if not self.student_id_var.get(): return messagebox.showwarning("Warning", "Please select a student first")
        self.edit_mode = True; self.original_student_id = self.student_id_var.get()
        self.set_fields_state("normal"); self.student_id_entry.config(state="normal")
        self.add_btn.config(state="disabled"); self.delete_btn.config(text="CANCEL", bg="#757575")
        self.update_btn.config(state="normal"); self.edit_label.config(text="EDIT MODE", fg="white", bg="red")

    def edit_student(self):
        error = self.validate()
        if error: return messagebox.showerror("Error", error)
        new_id = self.student_id_var.get()
        if new_id != self.original_student_id and self.student_id_exists(new_id): return messagebox.showerror("Error", "ID already exists")

        sql_parts = ["Student_name=%s", "grade_lvl=%s", "Guardian_name=%s", "Guardian_contact=%s", "Teacher_name=%s", "Student_id=%s", "fetcher_code=%s"]
        params = [self.student_name_var.get(), self.grade_var.get(), self.guardian_name_var.get(), 
                  self.guardian_contact_var.get(), self.teacher_name_var.get(), new_id, self.fetcher_code_var.get()]

        if self.photo_path is None: sql_parts.append("photo_path=NULL")
        elif not isinstance(self.photo_path, bytes):
            img = Image.open(self.photo_path).convert("RGB")
            img_byte_arr = io.BytesIO(); img.save(img_byte_arr, format='JPEG')
            sql_parts.append("photo_path=%s"); params.append(img_byte_arr.getvalue())

        params.append(self.original_student_id)
        query = f"UPDATE student SET {', '.join(sql_parts)} WHERE Student_id=%s"
        try:
            with db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params); conn.commit()
            messagebox.showinfo("Success", "Record updated"); self.reset_ui_state(); self.load_data()
        except Exception as e: messagebox.showerror("Error", f"Update failed: {e}")

    def delete_student(self):
        if self.delete_btn["text"] == "CANCEL": self.reset_ui_state(); return
        sid = self.student_id_var.get()
        if not sid: return messagebox.showwarning("Warning", "Select a student first")
        if not messagebox.askyesno("Confirm", "Delete this student?"): return
        try:
            with db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM student WHERE Student_id=%s", (sid,))
                    conn.commit()
            messagebox.showinfo("Success", "Record deleted"); self.reset_ui_state(); self.load_data()
        except Exception as e: messagebox.showerror("Error", f"Delete failed: {e}")

    def validate(self):
        if not self.student_name_var.get().strip(): return "Student Name is required"
        if not self.student_id_var.get().isdigit(): return "Student ID must be numeric"
        if not self.guardian_name_var.get().strip(): return "Guardian Name is required"
        return None

    def student_id_exists(self, student_id):
        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT Student_id FROM student WHERE Student_id=%s", (student_id,))
                return cursor.fetchone() is not None