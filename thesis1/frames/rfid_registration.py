import tkinter as tk
from tkinter import messagebox, ttk
import sys, os
import serial, threading, time
from PIL import Image, ImageTk

# ================= PATH SETUP =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.database import db_connect

class RfidRegistration(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#b2e5ed")
        self.controller = controller
        
        # State Variables
        self.selected_registration_id = None
        self.is_edit_mode = False
        self.fetcher_photo_path = None
        self.student_photo_path = None

        # ================= PAGINATION =================
        self.page_size = 15
        self.current_page = 1
        self.total_records = 0
        self.is_searching = False

        # ================= SERIAL SETUP =================
        self.ser = None
        self.start_serial_thread()

        # ================= HEADER =================
        header = tk.Frame(self, bg="#0047AB", height=65)
        header.pack(fill="x")
        tk.Label(header, text="RFID SYSTEM REGISTRATION",
                 font=("Arial", 20, "bold"), bg="#0047AB", fg="white").pack(side="left", padx=20, pady=15)

        # ================= SEARCH BAR =================
        search_frame = tk.Frame(self, bg="#b2e5ed")
        search_frame.pack(fill="x", padx=20, pady=10)
        
        self.search_var = tk.StringVar()
        self.search_ent = tk.Entry(search_frame, textvariable=self.search_var, font=("Arial", 12), width=40)
        self.search_ent.pack(side="left", padx=5)
        
        tk.Button(search_frame, text="🔍 Search", command=self.search_records).pack(side="left", padx=2)
        tk.Button(search_frame, text="Clear", command=self.reset_load).pack(side="left", padx=2)

        # ================= MAIN CONTENT =================
        main_container = tk.Frame(self, bg="#b2e5ed")
        main_container.pack(fill="both", expand=True, padx=20)

        # Left Panel: Forms & Photos
        left_panel = tk.Frame(main_container, bg="#b2e5ed")
        left_panel.pack(side="left", fill="y")

        # Variables
        self.rfid_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.contact_var = tk.StringVar()
        self.paired_rfid_var = tk.StringVar()

        self.student_rfid_var = tk.StringVar()
        self.student_id_var = tk.StringVar()
        self.student_name_var = tk.StringVar()
        self.grade_var = tk.StringVar()
        self.teacher_var = tk.StringVar()

        # Forms Row
        form_row = tk.Frame(left_panel, bg="#b2e5ed")
        form_row.pack()

        self.fetcher_entries = self.create_form(form_row, "FETCHER DETAILS", [
            ("RFID Tag", self.rfid_var),
            ("Name", self.name_var),
            ("Address", self.address_var),
            ("Contact", self.contact_var),
            ("Linked Tag", self.paired_rfid_var)
        ], 0)

        self.student_entries = self.create_form(form_row, "STUDENT DETAILS", [
            ("RFID Tag", self.student_rfid_var),
            ("Student ID", self.student_id_var),
            ("Name", self.student_name_var),
            ("Grade/Section", self.grade_var),
            ("Adviser", self.teacher_var)
        ], 1)

        # Photo Row
        photo_row = tk.Frame(left_panel, bg="#b2e5ed")
        photo_row.pack(pady=10)
        self.fetcher_photo_lbl = self.create_photo_box(photo_row, "Fetcher")
        self.student_photo_lbl = self.create_photo_box(photo_row, "Student")

        # Action Buttons
        btn_row = tk.Frame(left_panel, bg="#b2e5ed")
        btn_row.pack(pady=10)
        
        self.add_btn = tk.Button(btn_row, text="NEW PAIRING", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=15, command=self.toggle_add)
        self.add_btn.pack(side="left", padx=5)
        
        self.edit_btn = tk.Button(btn_row, text="EDIT RECORD", bg="#2196F3", fg="white", font=("Arial", 10, "bold"), width=15, command=self.toggle_edit)
        self.edit_btn.pack(side="left", padx=5)
        
        self.delete_btn = tk.Button(btn_row, text="DELETE", bg="#F44336", fg="white", font=("Arial", 10, "bold"), width=15, command=self.delete_record)
        self.delete_btn.pack(side="left", padx=5)

        # Right Panel: Table
        table_container = tk.Frame(main_container, bg="white", bd=1, relief="solid")
        table_container.pack(side="right", fill="both", expand=True, padx=(20, 0), pady=(0, 20))

        cols = ("id", "f_name", "s_name", "f_rfid", "s_rfid")
        self.table = ttk.Treeview(table_container, columns=cols, show="headings")
        self.table.heading("id", text="ID")
        self.table.heading("f_name", text="Fetcher")
        self.table.heading("s_name", text="Student")
        self.table.heading("f_rfid", text="F-RFID")
        self.table.heading("s_rfid", text="S-RFID")
        
        for col in cols:
            self.table.column(col, anchor="center")
        self.table.column("id", width=50)
        
        self.table.pack(fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.on_row_select)

        # Pagination Footer
        nav_frame = tk.Frame(table_container, bg="#f0f0f0")
        nav_frame.pack(fill="x")
        tk.Button(nav_frame, text="◀ PREV", command=self.prev_page).pack(side="left", padx=20, pady=5)
        self.page_lbl = tk.Label(nav_frame, text="Page 1", bg="#f0f0f0", font=("Arial", 10, "bold"))
        self.page_lbl.pack(side="left", expand=True)
        tk.Button(nav_frame, text="NEXT ▶", command=self.next_page).pack(side="right", padx=20, pady=5)

        self.lock_ui()
        self.load_data()

    # ================= UI BUILDERS =================
    def create_form(self, parent, title, fields, col):
        frame = tk.LabelFrame(parent, text=title, font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        frame.grid(row=0, column=col, padx=5, sticky="nsew")
        entries = []
        for i, (label, var) in enumerate(fields):
            tk.Label(frame, text=label, bg="white").grid(row=i, column=0, sticky="w", pady=2)
            ent = tk.Entry(frame, textvariable=var, font=("Arial", 11), width=25)
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

    # ================= STATE MANAGEMENT =================
    def lock_ui(self):
        self.is_edit_mode = False
        for e in self.fetcher_entries + self.student_entries:
            e.config(state="disabled")

    def unlock_ui(self):
        for e in self.fetcher_entries + self.student_entries:
            e.config(state="normal")

    def clear_all(self):
        self.selected_registration_id = None
        for var in [self.rfid_var, self.name_var, self.address_var, self.contact_var, 
                    self.paired_rfid_var, self.student_rfid_var, self.student_id_var, 
                    self.student_name_var, self.grade_var, self.teacher_var]:
            var.set("")
        self.fetcher_photo_lbl.config(image="", text="No Fetcher\nPhoto")
        self.student_photo_lbl.config(image="", text="No Student\nPhoto")

    # ================= SERIAL & RFID LOGIC =================
    def start_serial_thread(self):
        try:
            self.ser = serial.Serial("COM3", 9600, timeout=1)
            threading.Thread(target=self.serial_listener, daemon=True).start()
        except:
            print("RFID Reader not found on COM3.")

    def serial_listener(self):
        while self.ser and self.ser.is_open:
            try:
                line = self.ser.readline().decode().strip()
                if line:
                    self.after(0, lambda uid=line: self.handle_rfid_scan(uid))
            except: break

    def handle_rfid_scan(self, uid):
        if self.add_btn["text"] != "SAVE PAIR" and not self.is_edit_mode:
            return # Ignore scans if not in active mode

        # Logic: If Fetcher RFID is empty, fill it. Otherwise, fill Student RFID.
        if not self.rfid_var.get():
            self.rfid_var.set(uid)
            self.autofill_from_db("fetcher", uid)
        elif not self.student_rfid_var.get() and uid != self.rfid_var.get():
            self.student_rfid_var.set(uid)
            self.autofill_from_db("student", uid)
            self.paired_rfid_var.set(uid) # Automatically pair them

    def autofill_from_db(self, type, uid):
        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    if type == "fetcher":
                        cur.execute("SELECT Fetcher_name, Address, contact, photo_path FROM fetcher WHERE rfid_tag=%s", (uid,))
                        res = cur.fetchone()
                        if res:
                            self.name_var.set(res[0]); self.address_var.set(res[1])
                            self.contact_var.set(res[2]); self.show_img(res[3], self.fetcher_photo_lbl)
                    else:
                        cur.execute("SELECT name, student_id, grade, teacher, photo_path FROM students WHERE student_rfid=%s", (uid,))
                        res = cur.fetchone()
                        if res:
                            self.student_name_var.set(res[0]); self.student_id_var.set(res[1])
                            self.grade_var.set(res[2]); self.teacher_var.set(res[3]); self.show_img(res[4], self.student_photo_lbl)
        except Exception as e:
            print(f"Autofill error: {e}")

    def show_img(self, path, label):
        if path and os.path.exists(path):
            img = Image.open(path).resize((110, 110))
            photo = ImageTk.PhotoImage(img)
            label.config(image=photo, text="")
            label.image = photo

    # ================= CRUD OPERATIONS =================
    def toggle_add(self):
        if self.add_btn["text"] == "NEW PAIRING":
            self.clear_all()
            self.unlock_ui()
            self.add_btn.config(text="SAVE PAIR", bg="#2E7D32")
            self.edit_btn.config(state="disabled")
            self.delete_btn.config(text="CANCEL", bg="#757575")
        else:
            self.save_record()

    def toggle_edit(self):
        if not self.selected_registration_id:
            return messagebox.showwarning("Warning", "Please select a record to edit.")
        self.is_edit_mode = True
        self.unlock_ui()
        self.add_btn.config(state="disabled")
        self.edit_btn.config(text="UPDATE", bg="#FF9800")
        self.delete_btn.config(text="CANCEL", bg="#757575")

    def save_record(self):
        if not self.rfid_var.get() or not self.student_rfid_var.get():
            messagebox.showerror("Error", "Both RFID tags are required.")
            return

        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    if self.is_edit_mode:
                        cur.execute("""UPDATE registrations SET 
                            rfid=%s, fetcher_name=%s, student_rfid=%s, address=%s, contact=%s, 
                            student_id=%s, student_name=%s, grade=%s, teacher=%s, paired_rfid=%s 
                            WHERE registration_id=%s""",
                            (self.rfid_var.get(), self.name_var.get(), self.student_rfid_var.get(), 
                             self.address_var.get(), self.contact_var.get(), self.student_id_var.get(), 
                             self.student_name_var.get(), self.grade_var.get(), self.teacher_var.get(), 
                             self.student_rfid_var.get(), self.selected_registration_id))
                    else:
                        cur.execute("""INSERT INTO registrations 
                            (rfid, fetcher_name, student_rfid, address, contact, student_id, student_name, grade, teacher, paired_rfid)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                            (self.rfid_var.get(), self.name_var.get(), self.student_rfid_var.get(), 
                             self.address_var.get(), self.contact_var.get(), self.student_id_var.get(), 
                             self.student_name_var.get(), self.grade_var.get(), self.teacher_var.get(), 
                             self.student_rfid_var.get()))
                    conn.commit()
            messagebox.showinfo("Success", "Record saved successfully!")
            self.reset_load()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def delete_record(self):
        if self.delete_btn["text"] == "CANCEL":
            self.reset_load()
            return
        if not self.selected_registration_id: return
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this pairing?"):
            with db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM registrations WHERE registration_id=%s", (self.selected_registration_id,))
                    conn.commit()
            self.reset_load()

    # ================= DATA LOADING =================
    def load_data(self):
        self.table.delete(*self.table.get_children())
        offset = (self.current_page - 1) * self.page_size
        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM registrations")
                    self.total_records = cur.fetchone()[0]
                    
                    cur.execute("""SELECT registration_id, fetcher_name, student_name, rfid, student_rfid 
                                   FROM registrations ORDER BY registration_id DESC LIMIT %s OFFSET %s""", 
                                (self.page_size, offset))
                    for row in cur.fetchall():
                        self.table.insert("", "end", values=row)
            
            total_p = max(1, (self.total_records + self.page_size - 1) // self.page_size)
            self.page_lbl.config(text=f"Page {self.current_page} of {total_p}")
        except Exception as e:
            print(f"Table load error: {e}")

    def on_row_select(self, event):
        if self.is_edit_mode or self.add_btn["text"] == "SAVE PAIR": return
        selection = self.table.focus()
        if not selection: return
        
        item = self.table.item(selection, "values")
        self.selected_registration_id = item[0]
        
        with db_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM registrations WHERE registration_id=%s", (item[0],))
                r = cur.fetchone()
                if r:
                    self.rfid_var.set(r[1]); self.name_var.set(r[2])
                    self.student_rfid_var.set(r[3]); self.address_var.set(r[4])
                    self.contact_var.set(r[5]); self.student_id_var.set(r[6])
                    self.student_name_var.set(r[7]); self.grade_var.set(r[8])
                    self.teacher_var.set(r[9]); self.paired_rfid_var.set(r[10])
                    # Re-trigger photo display
                    self.autofill_from_db("fetcher", r[1])
                    self.autofill_from_db("student", r[3])

    def search_records(self):
        query = self.search_var.get().strip()
        if not query: return
        self.table.delete(*self.table.get_children())
        with db_connect() as conn:
            with conn.cursor() as cur:
                sql = """SELECT registration_id, fetcher_name, student_name, rfid, student_rfid 
                         FROM registrations WHERE fetcher_name LIKE %s OR student_name LIKE %s"""
                cur.execute(sql, (f"%{query}%", f"%{query}%"))
                for row in cur.fetchall():
                    self.table.insert("", "end", values=row)

    def reset_load(self):
        self.add_btn.config(text="NEW PAIRING", bg="#4CAF50", state="normal")
        self.edit_btn.config(text="EDIT RECORD", bg="#2196F3", state="normal")
        self.delete_btn.config(text="DELETE", bg="#F44336")
        self.current_page = 1
        self.lock_ui()
        self.clear_all()
        self.load_data()

    def next_page(self):
        if self.current_page * self.page_size < self.total_records:
            self.current_page += 1
            self.load_data()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()