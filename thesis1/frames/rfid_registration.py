import tkinter as tk
from tkinter import messagebox, ttk
import sys, os
import serial, threading, time
import serial.tools.list_ports
from PIL import Image, ImageTk
import io

# ================= PATH SETUP =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.database import db_connect

class RfidRegistration(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#b2e5ed")
        self.controller = controller
        
        # 1. State Variables (Define these FIRST)
        self.selected_registration_id = None
        self.is_edit_mode = False
        self.page_size = 15
        self.current_page = 1
        self.total_records = 0

        # 2. StringVars (These MUST exist before create_form is called)
        self.rfid_var = tk.StringVar()
        self.fetcher_code_var = tk.StringVar()
        self.fetcher_code_var.trace_add("write", lambda *a: self.autofill_record("fetcher"))
        self.fetcher_name_var = tk.StringVar()         
        self.fetcher_address_var = tk.StringVar()      
        self.fetcher_contact_var = tk.StringVar()      
        self.paired_rfid_var = tk.StringVar()  

        self.student_rfid_var = tk.StringVar() 
        self.student_id_var = tk.StringVar()
        self.student_id_var.trace_add("write", lambda *a: self.autofill_record("student"))
        self.student_name_var = tk.StringVar()
        self.guardian_name_var = tk.StringVar() 
        self.guardian_contact_var = tk.StringVar()
        self.grade_var = tk.StringVar()        
        self.teacher_var = tk.StringVar()
        self.search_var = tk.StringVar() # Moved search_var here too

        # 3. Serial Setup
        self.ser = None
        self.start_serial_thread()

        # 4. UI Layout (Now you can build the UI because variables exist)
        # ================= HEADER =================
        header = tk.Frame(self, bg="#0047AB", height=65)
        header.pack(fill="x")
        tk.Label(header, text="RFID SYSTEM REGISTRATION",
                 font=("Arial", 20, "bold"), bg="#0047AB", fg="white").pack(side="left", padx=20, pady=15)
        # ================= TOP SECTION: FORMS & PHOTOS =================
        top_container = tk.Frame(self, bg="#b2e5ed")
        top_container.pack(fill="x", padx=20, pady=10)

        # 1. Left Side: Fetcher Photo
        # We wrap the photo in a frame so it's easier to manage
        f_photo_frame = tk.Frame(top_container, bg="#b2e5ed")
        f_photo_frame.pack(side="left", padx=10)
        self.fetcher_photo_lbl = self.create_photo_box(f_photo_frame, "Fetcher")

        # 2. Center: Input Forms
        form_center_frame = tk.Frame(top_container, bg="#b2e5ed")
        form_center_frame.pack(side="left", expand=True)

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

        # 3. Right Side: Student Photo
        s_photo_frame = tk.Frame(top_container, bg="#b2e5ed")
        s_photo_frame.pack(side="right", padx=10)
        self.student_photo_lbl = self.create_photo_box(s_photo_frame, "Student")

        # ================= MIDDLE SECTION: BUTTONS & STATUS =================
        action_frame = tk.Frame(self, bg="#b2e5ed")
        action_frame.pack(fill="x", pady=5)

        self.status_var = tk.StringVar(value="Ready")
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

        # ================= BOTTOM SECTION: SEARCH & TABLE =================
        table_main_container = tk.Frame(self, bg="white", bd=1, relief="solid")
        table_main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Search Bar moved inside the table container for better grouping
        search_row = tk.Frame(table_main_container, bg="#f0f0f0")
        search_row.pack(fill="x", padx=5, pady=5)
        
        tk.Label(search_row, text="Search Records:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        tk.Entry(search_row, textvariable=self.search_var, font=("Arial", 12), width=30).pack(side="left", padx=5)
        tk.Button(search_row, text="🔍 Search", command=self.search_records).pack(side="left", padx=2)
        tk.Button(search_row, text="Clear", command=self.reset_load).pack(side="left", padx=2)

        self.count_var = tk.StringVar(value="Linked Students: 0")
        tk.Label(search_row, textvariable=self.count_var, font=("Arial", 10, "bold"), 
                 fg="#2E7D32", bg="#f0f0f0").pack(side="right", padx=10)

        # Treeview
        cols = ("id", "f_name", "s_name", "f_rfid", "s_rfid" , "status")
        self.table = ttk.Treeview(table_main_container, columns=cols, show="headings", height=10)
        self.table.heading("id", text="ID")
        self.table.heading("f_name", text="Fetcher")
        self.table.heading("s_name", text="Student")
        self.table.heading("f_rfid", text="F-RFID")
        self.table.heading("s_rfid", text="S-RFID")
        self.table.heading("status", text="Status")
        self.table.column("status", width=80, anchor="center")
        for col in cols: self.table.column(col, anchor="center")
        self.table.column("id", width=50)
        self.table.tag_configure("Active", foreground="green")
        self.table.tag_configure("Inactive", foreground="red")
        self.table.pack(fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.on_row_select)

        # Pagination
        nav_frame = tk.Frame(table_main_container, bg="#f0f0f0")
        nav_frame.pack(fill="x")
        tk.Button(nav_frame, text="◀ PREV", command=self.prev_page).pack(side="left", padx=20, pady=5)
        self.page_lbl = tk.Label(nav_frame, text="Page 1", bg="#f0f0f0", font=("Arial", 10, "bold"))
        self.page_lbl.pack(side="left", expand=True)
        tk.Button(nav_frame, text="NEXT ▶", command=self.next_page).pack(side="right", padx=20, pady=5)

    # ================= LOGIC METHODS =================

    def create_form(self, parent, title, fields, col):
        frame = tk.LabelFrame(parent, text=title, font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        frame.grid(row=0, column=col, padx=5, sticky="nsew")
        entries = []
        for i, (label, var) in enumerate(fields):
            tk.Label(frame, text=label, bg="white").grid(row=i, column=0, sticky="w", pady=2)
            state = "readonly" if "RFID" in label or "Tag" in label else "normal"
            ent = tk.Entry(frame, textvariable=var, font=("Arial", 11), width=25, state=state)
            ent.grid(row=i, column=1, pady=2, padx=5)
            entries.append(ent)
        return entries

    def create_photo_box(self, parent, label_text):
        container = tk.Frame(parent, bg="white", bd=1, relief="ridge", width=120, height=120)
        container.pack(side="left", padx=20)
        container.pack_propagate(False)
        lbl = tk.Label(container, text=f"No {label_text}\nPhoto", bg="white", font=("Arial", 8))
        lbl.pack(fill="both", expand=True)
        return lbl

    def start_serial_thread(self):
        def find_and_connect():
            ports = list(serial.tools.list_ports.comports())
            target_port = next((p.device for p in ports if any(x in p.description for x in ["USB", "CH340", "Arduino"])), "COM3")
            try:
                self.ser = serial.Serial(target_port, 9600, timeout=1)
                threading.Thread(target=self.serial_listener, daemon=True).start()
            except: pass
        threading.Thread(target=find_and_connect, daemon=True).start()

    def serial_listener(self):
        while self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if ":" in line: line = line.split(":")[-1].strip()
                    if line: self.after(0, lambda u=line: self.handle_rfid_scan(u))
            except: break
    # ================= REFINED RFID HANDLING =================
    def handle_rfid_scan(self, uid):
        """
        Logic: 
        1. If Fetcher RFID is empty, assign it.
        2. If Fetcher is filled but Student is empty, assign Student.
        3. Prevents duplicate scanning of the same tag for both roles.
        """
        if self.add_btn["text"] != "SAVE PAIR" and not self.is_edit_mode:
            return 
        
        # Step 1: Assign Fetcher Tag
        if not self.rfid_var.get():
            self.rfid_var.set(uid)
            self.status_var.set(f"✅ FETCHER TAG: {uid}")
            # Optional: Check if this tag is already in 'fetcher' table to autofill code
            self.find_owner_by_rfid(uid, "fetcher")
            
        # Step 2: Assign Student Tag (must be different from Fetcher Tag)
        elif not self.student_rfid_var.get():
            if uid == self.rfid_var.get():
                messagebox.showwarning("Warning", "You cannot use the same RFID for both Fetcher and Student.")
                return
                
            self.student_rfid_var.set(uid)
            self.paired_rfid_var.set(uid) 
            self.status_var.set(f"✅ STUDENT TAG: {uid}")
            # Optional: Check if this tag is already in 'student' table to autofill ID
            self.find_owner_by_rfid(uid, "student")

    # ================= DATABASE SYNC LOGIC =================
    def save_record(self):
        f_rfid = str(self.rfid_var.get()).strip()
        s_rfid = str(self.student_rfid_var.get()).strip()
        f_code = str(self.fetcher_code_var.get()).strip()
        s_id = str(self.student_id_var.get()).strip()

        if not all([f_rfid, s_rfid, f_code, s_id]):
            return messagebox.showerror("Missing Info", "Ensure both RFIDs are scanned and IDs are entered.")

        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    # 1. Update/Insert Registration Pairing
                    if self.is_edit_mode:
                        sql = """UPDATE registrations SET 
                                 rfid=%s, fetcher_name=%s, fetcher_code=%s, student_id=%s, 
                                 student_name=%s, grade=%s, teacher=%s, address=%s, 
                                 contact=%s, paired_rfid=%s, student_rfid=%s
                                 WHERE registration_id=%s"""
                        
                        cur.execute(sql, (f_rfid, self.fetcher_name_var.get(), f_code, s_id,
                                          self.student_name_var.get(), self.grade_var.get(),
                                          self.teacher_var.get(), self.fetcher_address_var.get(),
                                          self.fetcher_contact_var.get(), s_rfid, s_rfid, 
                                          self.selected_registration_id))
                    else:
                        sql = """INSERT INTO registrations (rfid, fetcher_name, fetcher_code, student_id, 
                                 student_name, grade, teacher, address, contact, paired_rfid, student_rfid, status) 
                                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, 'Active')"""
                        
                        cur.execute(sql, (f_rfid, self.fetcher_name_var.get(), f_code, s_id,
                                          self.student_name_var.get(), self.grade_var.get(),
                                          self.teacher_var.get(), self.fetcher_address_var.get(),
                                          self.fetcher_contact_var.get(), s_rfid, s_rfid))

                    # 2. CROSS-TABLE SYNC (THE FIX IS HERE)
                    # Note: Ensure these column names (rfid_tag) exist in your student/fetcher tables
                    # If you get an error here, check if the column is named 'rfid_tag' or 'student_rfid'
                    cur.execute("UPDATE student SET student_rfid=%s WHERE Student_id=%s", (s_rfid, s_id))
                    cur.execute("UPDATE fetcher SET rfid=%s WHERE fetcher_code=%s", (f_rfid, f_code))
                    
                    conn.commit()
            
            messagebox.showinfo("Success", "Pairing complete and Master Records Updated!")
            self.reset_load()
            
        except Exception as e:
            messagebox.showerror("Sync Error", f"Database error: {e}")
            
    def autofill_record(self, record_type="student", *args):
        if record_type == "student":
            search_id = self.student_id_var.get().strip()
            query = "SELECT * FROM student WHERE Student_id=%s"
            photo_lbl = self.student_photo_lbl
        else:
            search_id = self.fetcher_code_var.get().strip()
            query = "SELECT * FROM fetcher WHERE fetcher_code=%s"
            photo_lbl = self.fetcher_photo_lbl 

        if not search_id:
            self.clear_subfields(record_type)
            return

        try:
            with db_connect() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (search_id,))
                    data = cursor.fetchone()
                    
                    if data:
                        if record_type == "student":
                            self.student_name_var.set(data.get("Student_name", ""))
                            self.grade_var.set(data.get("grade_lvl", ""))
                            self.teacher_var.set(data.get("Teacher_name", ""))
                            self.guardian_name_var.set(data.get("Guardian_name", ""))
                            self.guardian_contact_var.set(data.get("Guardian_contact", ""))
                        else:
                            self.fetcher_name_var.set(data.get("Fetcher_name", ""))
                            self.fetcher_contact_var.set(data.get("contact", ""))
                            self.fetcher_address_var.set(data.get("Address", ""))

                        # Load Photo from BLOB
                        blob = data.get("photo_path")
                        if blob:
                            img = Image.open(io.BytesIO(blob)).resize((110, 110))
                            photo = ImageTk.PhotoImage(img)
                            photo_lbl.config(image=photo, text="")
                            photo_lbl.image = photo 
                        else:
                            photo_lbl.config(image="", text="NO PHOTO")
                    else:
                        self.clear_subfields(record_type, status="NOT FOUND")
        except Exception as e:
            print(f"Autofill Error: {e}")

    def update_student_count(self, name):
        try:
            with db_connect() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT COUNT(*) as total FROM registrations WHERE fetcher_name=%s", (name,))
                    count_res = cursor.fetchone()
                    self.count_var.set(f"Linked Students: {count_res['total']}")
        except: pass

    def on_row_select(self, event):
        selection = self.table.focus()
        if not selection: return
        item = self.table.item(selection, "values")
        self.selected_registration_id = item[0]
        
        with db_connect() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("""SELECT * FROM registrations WHERE registration_id=%s""", (item[0],))
                r = cur.fetchone()
                if r:
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
                    self.update_student_count(r['fetcher_name'])

    def load_data(self):
        self.table.delete(*self.table.get_children())
        offset = (self.current_page - 1) * self.page_size
        with db_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM registrations")
                self.total_records = cur.fetchone()[0]
            # Added status to the SELECT query
                cur.execute("""SELECT registration_id, fetcher_name, student_name, rfid, student_rfid, status 
                           FROM registrations ORDER BY registration_id DESC LIMIT %s OFFSET %s""", (self.page_size, offset))
            
                for row in cur.fetchall():
                # Apply the tag based on the status string (row[5])
                    self.table.insert("", "end", values=row, tags=(row[5],)) 
                
        total_p = max(1, (self.total_records + self.page_size - 1) // self.page_size)
        self.page_lbl.config(text=f"Page {self.current_page} of {total_p}")

    def lock_ui(self):
        for e in self.fetcher_entries + self.student_entries: e.config(state="disabled")
        self.is_edit_mode = False

    def unlock_ui(self):
        for e in self.fetcher_entries + self.student_entries:
            prop = str(e.cget("textvariable")).lower()
            e.config(state="readonly" if "rfid" in prop else "normal")

    def reset_load(self):
        self.add_btn.config(text="NEW PAIRING", bg="#4CAF50", state="normal")
        self.edit_btn.config(text="EDIT RECORD", bg="#2196F3", state="normal")
        self.delete_btn.config(text="DELETE", bg="#F44336")
        self.lock_ui(); self.clear_all(); self.load_data()

    def clear_all(self):
        vars_to_clear = [
            self.rfid_var, self.fetcher_name_var, self.fetcher_code_var, self.fetcher_address_var, self.fetcher_contact_var, 
            self.paired_rfid_var, self.student_rfid_var, self.student_id_var, 
            self.student_name_var, self.grade_var, self.teacher_var,
            self.guardian_name_var, self.guardian_contact_var, 
        ]
        for v in vars_to_clear: v.set("")
        self.count_var.set("Linked Students: 0")
        self.fetcher_photo_lbl.config(image="", text="No Fetcher\nPhoto")
        self.student_photo_lbl.config(image="", text="No Student\nPhoto")
        self.status_var.set("Ready")

    def toggle_add(self):
        if self.add_btn["text"] == "NEW PAIRING":
            self.clear_all(); self.unlock_ui(); self.add_btn.config(text="SAVE PAIR")
            self.delete_btn.config(text="CANCEL"); self.edit_btn.config(state="disabled")
        else: self.save_record()

    def toggle_edit(self):
        if not self.selected_registration_id: return
        self.is_edit_mode = True; self.unlock_ui(); self.edit_btn.config(text="UPDATE")
        self.add_btn.config(state="disabled"); self.delete_btn.config(text="CANCEL")

    def delete_record(self):
        if self.delete_btn["text"] == "CANCEL": self.reset_load(); return
        if self.selected_registration_id and messagebox.askyesno("Confirm", "Delete this record?"):
            with db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM registrations WHERE registration_id=%s", (self.selected_registration_id,))
                    conn.commit()
            self.reset_load()

    def search_records(self):
        q = f"%{self.search_var.get()}%"
        self.table.delete(*self.table.get_children())
        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    # Added 'status' to match the table's expected columns
                    cur.execute("""SELECT registration_id, fetcher_name, student_name, rfid, student_rfid, status 
                                   FROM registrations 
                                   WHERE fetcher_name LIKE %s OR student_name LIKE %s""", (q, q))
                    for row in cur.fetchall():
                        self.table.insert("", "end", values=row, tags=(row[5],))
        except Exception as e:
            print(f"Search Error: {e}")

    def next_page(self):
        if self.current_page * self.page_size < self.total_records: self.current_page += 1; self.load_data()

    def prev_page(self):
        if self.current_page > 1: self.current_page -= 1; self.load_data()

    def on_close(self):
        if self.ser and self.ser.is_open: self.ser.close()
        self.controller.destroy()

    def clear_subfields(self, record_type="student", status="NO PHOTO"):
        if record_type == "student":
            vars_to_clear = [self.student_name_var, self.grade_var, self.guardian_name_var, self.guardian_contact_var, self.teacher_var]
            lbl = self.student_photo_lbl
        else:
            vars_to_clear = [self.fetcher_name_var, self.fetcher_contact_var, self.fetcher_address_var]
            lbl = self.fetcher_photo_lbl
        for var in vars_to_clear: var.set("")
        lbl.config(image="", text=status)
        
    def start_listening(self):
        """Ensures the serial connection is active when the frame is shown."""
        if not self.ser or not self.ser.is_open:
            self.start_serial_thread()
        print("Serial listening started.")

    def stop_listening(self):
        """Safely closes the serial port when switching away from this frame."""
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
                self.ser = None # Reset to None so it can be restarted
                print("Serial port released.")
            except Exception as e:
                print(f"Error closing serial: {e}")
                
    def toggle_status(self):
        if not self.selected_registration_id:
            return messagebox.showwarning("Warning", "Please select a record from the table first.")

    # Get current status from table
        selection = self.table.focus()
        current_values = self.table.item(selection, "values")
        current_status = current_values[5] # index 5 is the status column

        new_status = "Inactive" if current_status == "Active" else "Active"
        confirm_msg = f"Mark ID as {new_status}?"
    
        if messagebox.askyesno("Confirm Status Change", confirm_msg):
            try:
                with db_connect() as conn:
                    with conn.cursor() as cur:
                    # Update database
                        cur.execute("UPDATE registrations SET status=%s WHERE registration_id=%s", 
                                (new_status, self.selected_registration_id))
                        conn.commit()
            
                messagebox.showinfo("Updated", f"Record is now {new_status}")
                self.load_data() # Refresh table
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update status: {e}")