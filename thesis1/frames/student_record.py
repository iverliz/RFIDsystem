import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import ImageTk, Image
import os
import sys
import time

# ================= PATH SETUP =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.database import db_connect

PHOTO_DIR = os.path.join(BASE_DIR, "student_photos")
os.makedirs(PHOTO_DIR, exist_ok=True)

# Define the path for your default placeholder image
DEFAULT_PHOTO = os.path.join(PHOTO_DIR, "default.png")
class StudentRecord(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#b2e5ed")
        self.controller = controller
        self.photo_path = None

        # ================= PAGINATION & SEARCH STATE =================
        self.page_size = 100
        self.current_page = 1
        self.total_students = 0
        self.search_results = [] # NEW: Stores results for search pagination
        self.search_page = 1     # NEW: Current page for search results

        # ================= VALIDATORS =================
        self.num_validate = self.register(self.only_numbers)
        self.contact_validate = self.register(self.contact_limit)

        # ================= HEADER =================
        header = tk.Frame(self, height=70, bg="#0047AB")
        header.pack(fill="x")

        tk.Label(
            header,
            text="STUDENT INFORMATION",
            font=("Arial", 20, "bold"),
            bg="#0047AB",
            fg="white"
        ).place(x=30, y=18)

        # ================= LEFT PANEL =================
        self.left_box = tk.Frame(self, width=430, height=480, bg="white", bd=2, relief="groove")
        self.left_box.place(x=40, y=90)
        self.left_box.pack_propagate(False)

        # ================= PHOTO =================
        self.photo_frame = tk.Frame(self.left_box, width=160, height=160, bg="#E0E0E0", bd=2, relief="ridge")
        self.photo_frame.place(x=20, y=20)
        self.photo_frame.pack_propagate(False)

        self.photo_label = tk.Label(self.photo_frame, bg="#E0E0E0")
        self.photo_label.pack(fill="both", expand=True)

        self.upload_btn = tk.Button(self.left_box, text="Upload Photo", width=14, command=self.upload_photo)
        self.upload_btn.place(x=210, y=80)
        
        self.remove_photo_btn = tk.Button(
            self.left_box, 
            text="Remove Photo", 
            width=14, 
            fg="red",
            command=self.remove_photo
        )
        self.remove_photo_btn.place(x=210, y=115) # Placed below Upload button
        self.remove_photo_btn.config(state="disabled")
        
        # Initially disable upload in VIEW MODE
        self.upload_btn.config(state="disabled")
        self.remove_photo_btn.config(state="disabled")

        # ================= VARIABLES =================
        self.student_name_var = tk.StringVar()
        self.grade_var = tk.StringVar()
        self.student_id_var = tk.StringVar()
        self.guardian_name_var = tk.StringVar()
        self.guardian_contact_var = tk.StringVar()
        self.teacher_name_var = tk.StringVar()

        self.guardian_contact_var.trace_add("write", self.format_contact)

        self.edit_mode = False
        self.original_student_id = None

        self.edit_label = tk.Label(
            self.left_box,
            text="VIEW MODE",
            font=("Arial", 10, "bold"),
            fg="gray",
            bg="white"
        )
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
            tk.Label(
                self.left_box,
                text=label,
                bg="white",
                font=("Arial", 11)
            ).place(x=20, y=y + i * 35)

            if label == "Grade:":
                entry = ttk.Spinbox(
                    self.left_box,
                    from_=1,
                    to=12,
                    textvariable=var,
                    width=28,
                    state="readonly"
                )

            elif label == "Student ID:":
                entry = tk.Entry(
                    self.left_box,
                    textvariable=var,
                    width=30,
                    font=("Arial", 11),
                    validate="key",
                    validatecommand=(self.num_validate, "%P")
                )
                self.student_id_entry = entry

            elif label == "Guardian Contact:":
                entry = tk.Entry(
                    self.left_box,
                    textvariable=var,
                    width=30,
                    font=("Arial", 11),
                    validate="key",
                    validatecommand=(self.contact_validate, "%P")
                )

            else:
                entry = tk.Entry(
                    self.left_box,
                    textvariable=var,
                    width=30,
                    font=("Arial", 11)
                )

            entry.place(x=150, y=y + i * 35)
            self.entries[label] = entry

        # ================= BUTTONS =================
        btn_frame = tk.Frame(self.left_box, bg="white")
        btn_frame.place(x=15, y=430)

        self.add_btn = tk.Button(
            btn_frame, text="ADD", width=9, bg="#4CAF50", fg="white",
            font=("Arial", 9, "bold"), command=self.add_student
        )
        self.add_btn.grid(row=0, column=0, padx=2)

        self.edit_btn = tk.Button(
            btn_frame, text="EDIT", width=9, bg="#2196F3", fg="white",
            font=("Arial", 9, "bold"), command=self.enable_edit_mode
        )
        self.edit_btn.grid(row=0, column=1, padx=2)

        self.update_btn = tk.Button(
            btn_frame, text="UPDATE", width=9, bg="#FF9800", fg="white",
            font=("Arial", 9, "bold"), command=self.edit_student,
            state="disabled"
        )
        self.update_btn.grid(row=0, column=2, padx=2)

        self.delete_btn = tk.Button(
            btn_frame, text="DELETE", width=9, bg="#F44336", fg="white",
            font=("Arial", 9, "bold"), command=self.delete_student
        )
        self.delete_btn.grid(row=0, column=3, padx=2)


        # ================= RIGHT PANEL =================
        self.right_panel = tk.Frame(self, width=500, height=480, bg="white", bd=2, relief="groove")
        self.right_panel.place(x=520, y=90)
        self.right_panel.pack_propagate(False)

        tk.Label(self.right_panel, text="Search Student", font=("Arial", 14, "bold"),
                 bg="white").place(x=20, y=15)

        self.search_var = tk.StringVar()
        tk.Entry(self.right_panel, textvariable=self.search_var,
                 width=25, font=("Arial", 11)).place(x=20, y=50)

        tk.Button(self.right_panel, text="Search",
                  command=self.search_student).place(x=260, y=47)
        
        # NEW: Clear Search button
        tk.Button(self.right_panel, text="Clear",
                  command=self.clear_search).place(x=320, y=47)

        self.count_var = tk.StringVar()
        tk.Label(self.right_panel, textvariable=self.count_var,
                 font=("Arial", 11, "bold"),
                 fg="#0047AB", bg="white").place(x=20, y=85)

        # ================= TABLE =================
        self.student_table = ttk.Treeview(
            self.right_panel,
            columns=("Student_id", "Student_name", "grade_lvl"),
            show="headings",
            height=12,
            takefocus=False
        )

        for col, txt, w in [
            ("Student_id", "Student ID", 120),
            ("Student_name", "Full Name", 220),
            ("grade_lvl", "Grade", 80)
        ]:
            self.student_table.heading(col, text=txt)
            self.student_table.column(col, width=w)

        self.student_table.place(x=20, y=120, width=450)
        self.student_table.bind("<<TreeviewSelect>>", self.on_table_select)
        self.student_table.bind("<Button-1>", self.clear_on_click, add="+")

        # ================= PAGINATION BUTTONS =================
        nav = tk.Frame(self.right_panel, bg="white")
        nav.place(x=160, y=420)

        tk.Button(nav, text="◀ Prev", command=self.prev_page).grid(row=0, column=0, padx=5)
        tk.Button(nav, text="Next ▶", command=self.next_page).grid(row=0, column=1, padx=5)

        # INITIALIZE STATE
        self.set_fields_state("disabled")
        self.display_photo(None)
        self.student_id_entry.config(state="disabled")
        self.load_data()
    
    def display_photo(self, path):
        """Displays photo or shows placeholder if path is invalid/missing."""
        try:
            if path and os.path.exists(path):
                img = Image.open(path).resize((160, 160))
                self.photo = ImageTk.PhotoImage(img)
                self.photo_label.config(image=self.photo, text="")
                self.photo_label.image = self.photo
            else:
                # DEFAULT LOGIC applied from Student Record
                self.photo_label.config(image="", text="NO PHOTO\nAVAILABLE", 
                                        font=("Arial", 10, "bold"), fg="#666666")
                self.photo = None
        except Exception:
            self.photo_label.config(image="", text="Error Loading Image")
            
    def upload_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if path:
            self.photo_path = path
            self.display_photo(path)

    def remove_photo(self):
        """Clears the selection and reverts to default."""
        self.photo_path = None
        self.display_photo(None)
    
    # ================= HELPERS & VALIDATION =================
    def only_numbers(self, v):
        return v.isdigit() or v == ""

    def contact_limit(self, v):
        return (v.isdigit() and len(v) <= 11) or v == ""

    def format_contact(self, *_):
        val = self.guardian_contact_var.get()
        if val.startswith("9") and len(val) == 10:
            self.guardian_contact_var.set("0" + val)

    def set_fields_state(self, state):
        """Standardizes how we enable/disable the form."""
        for label, entry in self.entries.items():
            if label == "Grade:":
                # Spinboxes need 'readonly' to prevent manual typing but allow clicking
                entry.config(state="readonly" if state == "disabled" else "normal")
            else:
                entry.config(state=state)
        self.upload_btn.config(state=state)
        self.remove_photo_btn.config(state=state)

    def reset_ui_state(self):
        """Returns buttons and labels to default VIEW MODE."""
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

    def validate(self):
        if not self.student_name_var.get().strip(): return "Student Name is required"
        if not self.student_id_var.get().isdigit(): return "Student ID must be numeric"
        if not self.grade_var.get().isdigit(): return "Grade must be numeric"
        if not self.guardian_name_var.get().strip(): return "Guardian Name is required"
        if not self.guardian_contact_var.get().isdigit(): return "Guardian Contact must be numeric"
        if not self.teacher_name_var.get().strip(): return "Teacher Name is required"
        return None

    def student_id_exists(self, student_id):
        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT Student_id FROM student WHERE Student_id=%s", (student_id,))
                return cursor.fetchone() is not None

    def clear_fields(self):
        for var in (self.student_name_var, self.student_id_var, self.grade_var,
                    self.guardian_name_var, self.guardian_contact_var, self.teacher_name_var):
            var.set("")
        self.photo_label.config(image="")
        self.photo_label.image = None
        self.photo_path = None
        self.student_table.selection_remove(self.student_table.selection())

    def clear_on_click(self, event):
        row_id = self.student_table.identify_row(event.y)
        if not row_id and not self.edit_mode and self.add_btn["text"] != "SAVE":
            self.clear_fields()

    # ================= CRUD FUNCTIONS =================
    def on_table_select(self, _):
        # Prevent selecting others while adding/editing
        if self.edit_mode or self.add_btn["text"] == "SAVE":
            return
            
        selected_items = self.student_table.selection()
        if not selected_items: 
            return

        selected = selected_items[0]
        student_id = self.student_table.item(selected, "values")[0]

        with db_connect() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM student WHERE Student_id=%s", (student_id,))
                student = cursor.fetchone()

        if student:
            # Fill text variables
            self.student_id_var.set(student["Student_id"])
            self.student_name_var.set(student["Student_name"])
            self.grade_var.set(student["grade_lvl"])
            self.guardian_name_var.set(student["Guardian_name"])
            self.guardian_contact_var.set(student["Guardian_contact"])
            self.teacher_name_var.set(student["Teacher_name"])

            # Handle photo via standardized method
            self.photo_path = student["photo_path"]
            self.display_photo(self.photo_path)

    def add_student(self):
        # STEP 1: If in View Mode, Switch to Add Mode
        if self.add_btn["text"] == "ADD":
            self.clear_fields()
            self.set_fields_state("normal")
            self.student_id_entry.config(state="normal")
            self.add_btn.config(text="SAVE", bg="#2E7D32")
            self.edit_btn.config(state="disabled")
            self.delete_btn.config(text="CANCEL", bg="#757575")
            return

        # STEP 2: If in Add Mode (SAVE clicked), process DB
        error = self.validate()
        if error: return messagebox.showerror("Error", error)
       

        sid = self.student_id_var.get()
        if self.student_id_exists(sid): return messagebox.showerror("Error", "ID already exists")

        img_save = None
        if self.photo_path and os.path.exists(self.photo_path):
            img_save = os.path.join(PHOTO_DIR, f"student_{sid}_{int(time.time())}.jpg")
            # Only save if it's not already in the target directory
            if not self.photo_path.startswith(PHOTO_DIR):
                Image.open(self.photo_path).convert("RGB").save(img_save)
            else:
                img_save = self.photo_path

        with db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""INSERT INTO student (Student_name, Student_id, grade_lvl, 
                               Guardian_name, Guardian_contact, Teacher_name, photo_path)
                               VALUES (%s,%s,%s,%s,%s,%s,%s)""", 
                               (self.student_name_var.get(), sid, self.grade_var.get(), 
                                self.guardian_name_var.get(), self.guardian_contact_var.get(), 
                                self.teacher_name_var.get(), img_save))
                conn.commit()

        messagebox.showinfo("Success", "Student added")
        self.reset_ui_state()
        self.load_data()

    def enable_edit_mode(self):
        if not self.student_id_var.get():
            return messagebox.showwarning("Warning", "Please select a student first")
        
        self.edit_mode = True
        self.original_student_id = self.student_id_var.get()
        self.set_fields_state("normal")
        self.student_id_entry.config(state="normal")
        
        self.add_btn.config(state="disabled")
        self.delete_btn.config(text="CANCEL", bg="#757575")
        self.update_btn.config(state="normal")
        self.edit_label.config(text="EDIT MODE", fg="white", bg="red")

    def edit_student(self):
        error = self.validate()
        if error: 
            return messagebox.showerror("Error", error)

        new_id = self.student_id_var.get()
        # Check if user is trying to change ID to one that already exists
        if new_id != self.original_student_id and self.student_id_exists(new_id):
            return messagebox.showerror("Error", "ID already exists")

        # Start building the SQL and Parameters dynamically
        sql_parts = [
            "Student_name=%s", "grade_lvl=%s", "Guardian_name=%s", 
            "Guardian_contact=%s", "Teacher_name=%s", "Student_id=%s"
        ]
        params = [
            self.student_name_var.get(), self.grade_var.get(), 
            self.guardian_name_var.get(), self.guardian_contact_var.get(), 
            self.teacher_name_var.get(), new_id
        ]

        # Handle Photo Update: Only save if a NEW photo was picked
        if self.photo_path and not self.photo_path.startswith(PHOTO_DIR):
            try:
                img_save = os.path.join(PHOTO_DIR, f"student_{new_id}_{int(time.time())}.jpg")
                # Convert to RGB handles PNG transparency/RGBA issues before saving as JPG
                Image.open(self.photo_path).convert("RGB").save(img_save)
                
                sql_parts.append("photo_path=%s")
                params.append(img_save)
            except Exception as e:
                return messagebox.showerror("Error", f"Failed to save image: {e}")

        # Finalize Query
        query = f"UPDATE student SET {', '.join(sql_parts)} WHERE Student_id=%s"
        params.append(self.original_student_id)
        
        try:
            with db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    conn.commit()
            
            messagebox.showinfo("Success", "Student record updated successfully")
            self.reset_ui_state()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Database Error", f"Update failed: {e}")
        
        
        
    def delete_student(self):
        # 1. Handle the "CANCEL" state first
        if self.delete_btn["text"] == "CANCEL":
            self.reset_ui_state()
            return

        # 2. Check if a student is actually selected
        sid = self.student_id_var.get()
        if not sid:
            return messagebox.showwarning("Warning", "Please select a student record from the table to delete.")

        # 3. Confirm with the user
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete Student ID: {sid}?\nThis will also delete their photo.")
        if not confirm:
            return

        try:
            with db_connect() as conn:
                with conn.cursor() as cursor:
                    # FETCH PHOTO PATH BEFORE DELETING THE ROW
                    cursor.execute("SELECT photo_path FROM student WHERE Student_id=%s", (sid,))
                    result = cursor.fetchone()
                    
                    # DELETE FROM DATABASE
                    cursor.execute("DELETE FROM student WHERE Student_id=%s", (sid,))
                    conn.commit()

            # 4. FILE SYSTEM CLEANUP
            # If a photo path exists and isn't the default image, delete it from the folder
            if result and result[0]:
                file_path = result[0]
                if os.path.exists(file_path) and file_path != DEFAULT_PHOTO:
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"File deletion error: {e}") # Non-critical error, just log it

            messagebox.showinfo("Success", f"Record for Student {sid} has been deleted.")
            self.clear_fields()
            self.load_data()

        except Exception as e:
            messagebox.showerror("Database Error", f"Could not delete record: {e}")

    # ================= SMART PAGINATION & SEARCH =================
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
                    for row in cursor.fetchall(): 
                        self.student_table.insert("", "end", values=row)

            total_p = max(1, (self.total_students + self.page_size - 1) // self.page_size)
            self.count_var.set(f"Students: {self.total_students} | Page {self.current_page}/{total_p}")

        except Exception as e:
            messagebox.showerror("Database Error", f"Could not load data: {e}")
        
    def search_student(self):
        keyword = self.search_var.get().strip()
        
        # If the search box is empty, just reload the full list
        if not keyword: 
            return self.clear_search()

        try:
            with db_connect() as conn:
                with conn.cursor() as cursor:
                    # Using LOWER() and LIKE for better matching
                    query = """SELECT Student_id, Student_name, grade_lvl FROM student 
                               WHERE Student_name LIKE %s OR Student_id LIKE %s"""
                    cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
                    self.search_results = cursor.fetchall()

            if not self.search_results:
                self.student_table.delete(*self.student_table.get_children())
                self.count_var.set("No results found.")
                return

            # Reset search pagination to page 1
            self.search_page = 1
            self.update_search_table()
            
        except Exception as e:
            messagebox.showerror("Search Error", f"An error occurred: {e}")

     
    def update_search_table(self):
        """Refreshes the Treeview with search results based on current search_page."""
        self.student_table.delete(*self.student_table.get_children())
        
        start = (self.search_page - 1) * self.page_size
        end = start + self.page_size
        
        page_data = self.search_results[start:end]
        for row in page_data: 
            self.student_table.insert("", "end", values=row)
        
        total_p = max(1, (len(self.search_results) + self.page_size - 1) // self.page_size)
        self.count_var.set(f"Matches: {len(self.search_results)} | Page {self.search_page}/{total_p}")

    def clear_search(self):
        self.search_var.set("")
        self.search_results = []
        self.current_page = 1 
        self.load_data()

    def next_page(self):
        # Determine if we are navigating Search Results or the Full List
        is_searching = bool(self.search_var.get().strip())

        if is_searching:
            if self.search_page * self.page_size < len(self.search_results):
                self.search_page += 1
                self.update_search_table()
        else:
            if self.current_page * self.page_size < self.total_students:
                self.current_page += 1
                self.load_data()

    def prev_page(self):
        is_searching = bool(self.search_var.get().strip())

        if is_searching:
            if self.search_page > 1: 
                self.search_page -= 1
                self.update_search_table()
        else:
            if self.current_page > 1:
                self.current_page -= 1
                self.load_data()