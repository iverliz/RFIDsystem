import tkinter as tk
from tkinter import messagebox, ttk
import sys, os
from PIL import Image, ImageTk
import io

# ================= PATH SETUP =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from utils.database import db_connect

class RfidRegistration(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#b2e5ed")
        self.controller = controller
        
        # State Management
        self.selected_registration_id = None
        self.is_edit_mode = False
        self.page_size = 15
        self.current_page = 1
        self.total_records = 0

        # Define Variables
        self.rfid_var = tk.StringVar()
        self.fetcher_code_var = tk.StringVar()
        self.fetcher_name_var = tk.StringVar()         
        self.fetcher_address_var = tk.StringVar()      
        self.fetcher_contact_var = tk.StringVar()      
        self.paired_rfid_var = tk.StringVar()  

        self.student_rfid_var = tk.StringVar() 
        self.student_id_var = tk.StringVar()
        self.student_name_var = tk.StringVar()
        self.guardian_name_var = tk.StringVar() 
        self.guardian_contact_var = tk.StringVar()
        self.grade_var = tk.StringVar()        
        self.teacher_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="System Ready")
        self.count_var = tk.StringVar(value="Linked Students: 0")

        # Traces for Autofill
        self.fetcher_code_var.trace_add("write", lambda *a: self.autofill_record("fetcher"))
        self.student_id_var.trace_add("write", lambda *a: self.autofill_record("student"))

        self.setup_ui()
        self.reset_load()

    def setup_ui(self):
        # Header
        header = tk.Frame(self, bg="#0047AB", height=65)
        header.pack(fill="x")
        tk.Label(header, text="RFID SYSTEM REGISTRATION",
                 font=("Arial", 20, "bold"), bg="#0047AB", fg="white").pack(side="left", padx=20, pady=15)
        
        top_container = tk.Frame(self, bg="#b2e5ed")
        top_container.pack(fill="x", padx=20, pady=10)

        # Photo Boxes
        f_photo_frame = tk.Frame(top_container, bg="#b2e5ed")
        f_photo_frame.pack(side="left", padx=10)
        self.fetcher_photo_lbl = self.create_photo_box(f_photo_frame, "Fetcher")

        form_center_frame = tk.Frame(top_container, bg="#b2e5ed")
        form_center_frame.pack(side="left", expand=True)

        # Forms
        self.fetcher_entries = self.create_form(form_center_frame, "FETCHER DETAILS", [
            ("RFID Tag", self.rfid_var),
            ("Name", self.fetcher_name_var),          
            ("Fetcher Code", self.fetcher_code_var),
            ("Address", self.fetcher_address_var),   
            ("Contact", self.fetcher_contact_var),   
            ("Linked Tag", self.paired_rfid_var)
        ], 0)

        self.student_entries = self.create_form(form_center_frame, "STUDENT DETAILS", [
            ("RFID Tag", self.student_rfid_var),
            ("Student ID", self.student_id_var),
            ("Name", self.student_name_var),
            ("Grade/Section", self.grade_var),
            ("Guardian Name", self.guardian_name_var),
            ("Guardian Contact", self.guardian_contact_var),
            ("Adviser", self.teacher_var)
        ], 1)

        s_photo_frame = tk.Frame(top_container, bg="#b2e5ed")
        s_photo_frame.pack(side="right", padx=10)
        self.student_photo_lbl = self.create_photo_box(s_photo_frame, "Student")

        # Action Buttons
        action_frame = tk.Frame(self, bg="#b2e5ed")
        action_frame.pack(fill="x", pady=5)
        tk.Label(action_frame, textvariable=self.status_var, font=("Arial", 10, "italic"), 
                 fg="#0047AB", bg="#b2e5ed").pack()

        btn_row = tk.Frame(action_frame, bg="#b2e5ed")
        btn_row.pack(pady=5)

        self.add_btn = tk.Button(btn_row, text="NEW PAIRING", bg="#4CAF50", fg="white", 
                                font=("Arial", 10, "bold"), width=15, command=self.toggle_add)
        self.add_btn.pack(side="left", padx=5)
        
        self.edit_btn = tk.Button(btn_row, text="EDIT RECORD", bg="#2196F3", fg="white", 
                                 font=("Arial", 10, "bold"), width=15, command=self.toggle_edit)
        self.edit_btn.pack(side="left", padx=5)
        
        self.delete_btn = tk.Button(btn_row, text="DELETE", bg="#F44336", fg="white", 
                                   font=("Arial", 10, "bold"), width=15, command=self.delete_record)
        self.delete_btn.pack(side="left", padx=5)
        
        self.status_btn = tk.Button(btn_row, text="TOGGLE STATUS", bg="#607D8B", fg="white", 
                                font=("Arial", 10, "bold"), width=15, command=self.toggle_status)
        self.status_btn.pack(side="left", padx=5)

        # Table Section
        table_main_container = tk.Frame(self, bg="white", bd=1, relief="solid")
        table_main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        search_row = tk.Frame(table_main_container, bg="#f0f0f0")
        search_row.pack(fill="x", padx=5, pady=5)
        tk.Label(search_row, text="Search:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Entry(search_row, textvariable=self.search_var, font=("Arial", 11)).pack(side="left", padx=5)
        tk.Button(search_row, text="🔍", command=self.search_records).pack(side="left")
        tk.Button(search_row, text="Reset", command=self.reset_load).pack(side="left", padx=5)
        tk.Label(search_row, textvariable=self.count_var, font=("Arial", 10, "bold"), bg="#f0f0f0", fg="green").pack(side="right", padx=10)

        cols = ("id", "f_name", "s_name", "f_rfid", "s_rfid" , "status")
        self.table = ttk.Treeview(table_main_container, columns=cols, show="headings", height=10)
        for col in cols:
            self.table.heading(col, text=col.upper())
            self.table.column(col, anchor="center")
        self.table.pack(fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.on_row_select)

    # ================= FUNCTIONAL LOGIC =================

    def handle_rfid_scan(self, uid): 
        """Called by main.py whenever a tag is read"""
        if not self.is_edit_mode and self.add_btn["text"] != "SAVE PAIR":
            return 

        if not self.rfid_var.get():
            self.rfid_var.set(uid)
            self.status_var.set(f"✅ FETCHER TAG: {uid}")
            self.find_owner_by_rfid(uid, "fetcher")
        elif not self.student_rfid_var.get():
            if uid == self.rfid_var.get():
                messagebox.showwarning("Warning", "UID already assigned to Fetcher.")
                return
            self.student_rfid_var.set(uid)
            self.paired_rfid_var.set(uid) 
            self.status_var.set(f"✅ STUDENT TAG: {uid}")
            self.find_owner_by_rfid(uid, "student")

    def save_record(self):
        # 1. Collect Data from UI Variables
        f_rfid = self.rfid_var.get().strip()
        s_rfid = self.student_rfid_var.get().strip()
        f_code = self.fetcher_code_var.get().strip()
        s_id = self.student_id_var.get().strip()
        
        # Collect other fields (ensure these variables exist in your class)
        f_name = self.fetcher_name_var.get().strip()
        s_name = self.student_name_var.get().strip()
        grade = self.grade_var.get().strip()
        teacher = self.teacher_var.get().strip()
        address = self.fetcher_address_var.get().strip()
        contact = self.fetcher_contact_var.get().strip()

        # 2. Validation
        if not all([f_rfid, s_rfid, f_code, s_id, f_name, s_name]):
            messagebox.showerror("Error", "All required fields must be filled.")
            return

        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    
                    # --- DUPLICATE PROTECTION LOGIC ---
                    # Logic: We allow the SAME Fetcher RFID for DIFFERENT Students (Siblings).
                    # But we NEVER allow the SAME Student RFID for different records.
                    
                    check_sql = "SELECT student_name FROM registrations WHERE student_rfid = %s"
                    params = [s_rfid]
                    
                    if self.is_edit_mode:
                        check_sql += " AND registration_id != %s"
                        params.append(self.selected_registration_id)
                    
                    cur.execute(check_sql, tuple(params))
                    existing_student = cur.fetchone()
                    
                    if existing_student:
                        messagebox.showerror("Duplicate Student Card", 
                            f"This Student RFID is already assigned to: {existing_student[0]}")
                        return
                    # ----------------------------------

                    if self.is_edit_mode:
                        # Update existing record
                        sql = """UPDATE registrations SET 
                                 rfid=%s, fetcher_name=%s, fetcher_code=%s, 
                                 student_id=%s, student_name=%s, grade=%s, 
                                 teacher=%s, address=%s, contact=%s, 
                                 paired_rfid=%s, student_rfid=%s 
                                 WHERE registration_id=%s"""
                        cur.execute(sql, (f_rfid, f_name, f_code, s_id, s_name, 
                                          grade, teacher, address, contact, 
                                          s_rfid, s_rfid, self.selected_registration_id))
                    else:
                        # Insert new record
                        sql = """INSERT INTO registrations (
                                 rfid, fetcher_name, fetcher_code, student_id, 
                                 student_name, grade, teacher, address, 
                                 contact, paired_rfid, student_rfid, status
                                 ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, 'Active')"""
                        cur.execute(sql, (f_rfid, f_name, f_code, s_id, s_name, 
                                          grade, teacher, address, contact, 
                                          s_rfid, s_rfid))
                    
                    conn.commit()

            # --- SUCCESS & LINKING PROMPT ---
            messagebox.showinfo("Success", f"Successfully registered {s_name}.")
            
            # Ask to link a sibling
            link_sibling = messagebox.askyesno("Link Sibling", 
                f"Do you want to link another student to Fetcher: {f_name}?")
            
            if link_sibling:
                # KEEP Fetcher Info, CLEAR Student Info
                self.student_id_var.set("")
                self.student_name_var.set("")
                self.student_rfid_var.set("")
                
                # Update UI state for a new entry even if we were just editing
                self.is_edit_mode = False 
                self.mode_label.config(text="LINKING NEW SIBLING", bg="#fff9c4", fg="#fbc02d")
                
                # Focus on the next student ID to scan
                if hasattr(self, 'student_id_entry'):
                    self.student_id_entry.focus_set()
            else:
                # Reset the whole form if no more siblings
                self.reset_load() 

        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    def autofill_record(self, record_type):
        search_id = self.student_id_var.get().strip() if record_type == "student" else self.fetcher_code_var.get().strip()
        if not search_id: return self.clear_subfields(record_type)

        query = "SELECT * FROM student WHERE Student_id=%s" if record_type == "student" else "SELECT * FROM fetcher WHERE fetcher_code=%s"
        try:
            with db_connect() as conn:
                with conn.cursor(dictionary=True) as cur:
                    cur.execute(query, (search_id,))
                    data = cur.fetchone()
                    if data:
                        if record_type == "student":
                            self.student_name_var.set(data.get("Student_name", ""))
                            self.grade_var.set(data.get("grade_lvl", ""))
                            self.teacher_var.set(data.get("Teacher_name", ""))
                        else:
                            self.fetcher_name_var.set(data.get("Fetcher_name", ""))
                            self.fetcher_contact_var.set(data.get("contact", ""))
                        
                        # Handle Photo
                        blob = data.get("photo_path")
                        lbl = self.student_photo_lbl if record_type == "student" else self.fetcher_photo_lbl
                        if blob:
                            img = Image.open(io.BytesIO(blob)).resize((110, 110))
                            photo = ImageTk.PhotoImage(img)
                            lbl.config(image=photo, text="")
                            lbl.image = photo
                    else:
                        self.clear_subfields(record_type, "NOT FOUND")
        except Exception as e:
            print(f"Autofill error: {e}")

    def find_owner_by_rfid(self, rfid_uid, target_type):
        """Cross-references a scanned tag with master tables"""
        table = "fetcher" if target_type == "fetcher" else "student"
        col_rfid = "rfid" if target_type == "fetcher" else "student_rfid"
        col_id = "fetcher_code" if target_type == "fetcher" else "Student_id"
        
        try:
            with db_connect() as conn:
                with conn.cursor(dictionary=True) as cur:
                    cur.execute(f"SELECT {col_id} FROM {table} WHERE {col_rfid}=%s", (rfid_uid,))
                    res = cur.fetchone()
                    if res:
                        if target_type == "fetcher": self.fetcher_code_var.set(res[col_id])
                        else: self.student_id_var.set(res[col_id])
        except Exception as e:
            print(f"Lookup Error: {e}")

    # ================= UI HELPERS =================

    def create_form(self, parent, title, fields, col):
        frame = tk.LabelFrame(parent, text=title, font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        frame.grid(row=0, column=col, padx=5, sticky="nsew")
        entries = []
        for i, (label, var) in enumerate(fields):
            tk.Label(frame, text=label, bg="white").grid(row=i, column=0, sticky="w")
            ent = tk.Entry(frame, textvariable=var, font=("Arial", 11), width=22)
            ent.grid(row=i, column=1, pady=2, padx=5)
            entries.append(ent)
        return entries

    def create_photo_box(self, parent, label_text):
        container = tk.Frame(parent, bg="white", bd=1, relief="ridge", width=120, height=120)
        container.pack(padx=10, pady=10); container.pack_propagate(False)
        lbl = tk.Label(container, text=f"No {label_text}\nPhoto", bg="white")
        lbl.pack(fill="both", expand=True)
        return lbl

    def reset_load(self):
        self.clear_all()
        self.lock_ui()
        self.is_edit_mode = False
        self.selected_registration_id = None
        self.add_btn.config(text="NEW PAIRING", state="normal")
        self.edit_btn.config(text="EDIT RECORD", state="normal")
        self.delete_btn.config(text="DELETE")
        self.load_data()

    def lock_ui(self):
        for e in self.fetcher_entries + self.student_entries: e.config(state="disabled")

    def unlock_ui(self):
        for e in self.fetcher_entries + self.student_entries:
            var_name = str(e.cget("textvariable")).lower()
            e.config(state="readonly" if "rfid" in var_name else "normal")

    def toggle_add(self):
        if self.add_btn["text"] == "NEW PAIRING":
            self.clear_all(); self.unlock_ui()
            self.add_btn.config(text="SAVE PAIR")
            self.delete_btn.config(text="CANCEL")
            self.status_var.set("Waiting for RFID Scan...")
        else:
            self.save_record()

    def toggle_edit(self):
        if not self.selected_registration_id:
            messagebox.showwarning("Warning", "Please select a record from the table first!")
            return
        
        # Change state to Edit Mode
        self.is_edit_mode = True
        self.unlock_ui()
        
        # Update Button UI
        self.edit_btn.config(text="UPDATE", bg="#FF9800") # Change color to orange for visibility
        self.add_btn.config(state="disabled")
        self.delete_btn.config(text="CANCEL")
        self.status_var.set("EDIT MODE: Modify fields and click UPDATE")

    def clear_all(self):
        for var in [self.rfid_var, self.student_rfid_var, self.fetcher_code_var, self.student_id_var, 
                    self.fetcher_name_var, self.student_name_var, self.grade_var, self.teacher_var,
                    self.fetcher_address_var, self.fetcher_contact_var, self.paired_rfid_var]:
            var.set("")
        self.fetcher_photo_lbl.config(image="", text="No Photo")
        self.student_photo_lbl.config(image="", text="No Photo")

    def clear_subfields(self, record_type, status="NO PHOTO"):
        lbl = self.student_photo_lbl if record_type == "student" else self.fetcher_photo_lbl
        lbl.config(image="", text=status)

    def load_data(self):
        self.table.delete(*self.table.get_children())
        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT registration_id, fetcher_name, student_name, rfid, student_rfid, status FROM registrations")
                    for row in cur.fetchall():
                        self.table.insert("", "end", values=row)
        except Exception as e: print(f"Load Error: {e}")

    def on_row_select(self, event):
        selection = self.table.focus()
        if not selection: 
            return
            
        # Get the Registration ID from the first column of the selected row
        item = self.table.item(selection, "values")
        self.selected_registration_id = item[0]
        
        try:
            with db_connect() as conn:
                with conn.cursor(dictionary=True) as cur:
                    cur.execute("SELECT * FROM registrations WHERE registration_id=%s", (self.selected_registration_id,))
                    r = cur.fetchone()
                    
                    if r:
                        # Populate all variables with the database record
                        self.rfid_var.set(r['rfid'])
                        self.fetcher_name_var.set(r['fetcher_name'])
                        self.fetcher_code_var.set(r['fetcher_code'])
                        self.student_id_var.set(r['student_id'])
                        self.student_name_var.set(r['student_name'])
                        self.grade_var.set(r['grade'])
                        self.teacher_var.set(r['teacher'])
                        self.fetcher_address_var.set(r['address'])
                        self.fetcher_contact_var.set(r['contact'])
                        self.paired_rfid_var.set(r['paired_rfid'])
                        self.student_rfid_var.set(r['student_rfid'])
                        
                        # Update student count label
                        self.update_student_count(r['fetcher_name'])
                        self.status_var.set(f"Selected Record ID: {self.selected_registration_id}")
        except Exception as e:
            print(f"Error selecting row: {e}")

    def delete_record(self):
        if self.delete_btn["text"] == "CANCEL": return self.reset_load()
        if not self.selected_registration_id: return
        if messagebox.askyesno("Confirm", "Delete record?"):
            with db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM registrations WHERE registration_id=%s", (self.selected_registration_id,))
                    conn.commit()
            self.reset_load()

    def toggle_status(self):
        # Implementation to switch Active/Inactive
        pass

    def search_records(self):
        q = f"%{self.search_var.get()}%"
        self.table.delete(*self.table.get_children())
        with db_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT registration_id, fetcher_name, student_name, rfid, student_rfid, status FROM registrations WHERE fetcher_name LIKE %s OR student_name LIKE %s", (q, q))
                for row in cur.fetchall(): self.table.insert("", "end", values=row)
                
    def update_student_count(self, name):
        try:
            with db_connect() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT COUNT(*) as total FROM registrations WHERE fetcher_name=%s", (name,))
                    count_res = cursor.fetchone()
                    self.count_var.set(f"Linked Students: {count_res['total']}")
        except: 
            pass