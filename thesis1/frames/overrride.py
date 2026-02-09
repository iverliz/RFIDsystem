import tkinter as tk
from tkinter import messagebox, ttk
import os
import sys

# Ensure utility imports work
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from utils.database import db_connect

class OverrideFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#b2e5ed")
        self.controller = controller
        self.editing_mode = False 
        
        # --- UI Header ---
        header = tk.Frame(self, bg="#0047AB", height=60)
        header.pack(fill="x")
        tk.Label(header, text="MASTER RFID MANAGEMENT", font=("Arial", 18, "bold"), 
                 bg="#0047AB", fg="white").pack(pady=10)

        # --- Main Layout ---
        main_container = tk.Frame(self, bg="#b2e5ed")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # --- LEFT SIDE: Form ---
        self.form_container = tk.Frame(main_container, bg="white", padx=20, pady=20, 
                                       highlightthickness=2, highlightbackground="#CCCCCC")
        self.form_container.pack(side="left", fill="y", padx=(0, 20))

        # Edit Mode Indicator
        self.mode_label = tk.Label(self.form_container, text="🆕 NEW REGISTRATION", 
                                   font=("Arial", 10, "bold"), bg="#e8f5e9", fg="#2e7d32", pady=5)
        self.mode_label.pack(fill="x", pady=(0, 15))

        tk.Label(self.form_container, text="Teacher Employee ID:", bg="white", font=("Arial", 9, "bold")).pack(anchor="w")
        self.emp_id_entry = tk.Entry(self.form_container, font=("Arial", 11), width=25, bd=1, relief="solid")
        self.emp_id_entry.pack(pady=(5, 15), ipady=3)

        tk.Label(self.form_container, text="RFID UID (Tap Card):", bg="white", 
                 font=("Arial", 9, "bold"), fg="#0047AB").pack(anchor="w")
        self.rfid_entry = tk.Entry(self.form_container, font=("Arial", 11), width=25, bd=1, 
                                   relief="solid", justify="center")
        self.rfid_entry.pack(pady=(5, 10), ipady=3)
        self.rfid_entry.bind("<Return>", lambda e: self.handle_save())

        # Buttons
        self.save_btn = tk.Button(self.form_container, text="➕ REGISTER CARD", command=self.handle_save, 
                                  bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), width=20, pady=8, bd=0)
        self.save_btn.pack(pady=5)
        
        # Initialize Cancel Button (Hidden by default)
        self.cancel_btn = tk.Button(self.form_container, text="✖ CANCEL EDIT", command=self.clear_form, 
                                    bg="#757575", fg="white", font=("Arial", 9, "bold"), width=20, pady=5, bd=0)
        
        self.del_btn = tk.Button(self.form_container, text="🗑️ DELETE RECORD", command=self.handle_delete, 
                                 bg="#f44336", fg="white", font=("Arial", 9, "bold"), width=20, pady=8, bd=0)
        self.del_btn.pack(pady=5)

        # --- RIGHT SIDE: List ---
        list_container = tk.Frame(main_container, bg="white", padx=10, pady=10, 
                                  highlightthickness=1, highlightbackground="#CCCCCC")
        list_container.pack(side="right", fill="both", expand=True)

        list_header = tk.Frame(list_container, bg="white")
        list_header.pack(fill="x", pady=(0, 10))
        tk.Label(list_header, text="Registered Master Overrides", font=("Arial", 11, "bold"), bg="white").pack(side="left")
        
        tk.Button(list_header, text="✅ ACTIVATE", bg="#2196F3", fg="white", font=("Arial", 8, "bold"), 
                  command=lambda: self.toggle_status("Active")).pack(side="right", padx=2)
        tk.Button(list_header, text="🚫 DEACTIVATE", bg="#FF9800", fg="white", font=("Arial", 8, "bold"), 
                  command=lambda: self.toggle_status("Deactivated")).pack(side="right", padx=2)

        self.tree = ttk.Treeview(list_container, columns=("EID", "Name", "UID", "Status"), show="headings", height=15)
        self.tree.heading("EID", text="Emp ID"); self.tree.heading("Name", text="Teacher Name")
        self.tree.heading("UID", text="RFID UID"); self.tree.heading("Status", text="Status")
        self.tree.column("EID", width=70, anchor="center")
        self.tree.column("Status", width=100, anchor="center")
        self.tree.pack(fill="both", expand=True)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
        self.refresh_list()
        
        # SET INITIAL FOCUS so RFID scanning works immediately
        self.emp_id_entry.focus_set()

    # --- KEY FIXES ---

    def handle_rfid_tap(self, uid):
        """Force the entry to update even if it was previously locked."""
        # 1. Unlock temporarily
        self.rfid_entry.config(state="normal") 
        
        # 2. Update value
        self.rfid_entry.delete(0, tk.END)
        self.rfid_entry.insert(0, uid)
        
        # 3. Visual feedback
        self.rfid_entry.config(bg="#e8f5e9") 
        self.after(500, lambda: self.rfid_entry.config(bg="white"))
        
        # 4. If in editing mode, keep it readonly after update to protect the ID
        if self.editing_mode:
            self.rfid_entry.focus_set()

    def on_item_select(self, event):
        selected = self.tree.focus()
        if not selected: return
            
        values = self.tree.item(selected, "values")
        teacher_id, teacher_name = values[0], values[1]

        # Toggle Edit Mode
        self.editing_mode = True
        self.mode_label.config(text=f"✏️ EDITING: {teacher_name}", bg="#fff3e0", fg="#e65100")
        self.form_container.config(highlightbackground="#FF9800")
        
        self.save_btn.config(text="💾 UPDATE CHANGES", bg="#FF9800")
        self.cancel_btn.pack(after=self.save_btn, pady=5) # Show cancel button

        self.emp_id_entry.delete(0, tk.END)
        self.emp_id_entry.insert(0, teacher_id)
        self.emp_id_entry.config(state="readonly") # Prevent changing ID during edit
        
        self.rfid_entry.delete(0, tk.END)
        self.rfid_entry.insert(0, values[2])
        self.rfid_entry.focus_set()

    def clear_form(self):
        self.editing_mode = False
        self.mode_label.config(text="🆕 NEW REGISTRATION", bg="#e8f5e9", fg="#2e7d32")
        self.form_container.config(highlightbackground="#CCCCCC")
        self.save_btn.config(text="➕ REGISTER CARD", bg="#4CAF50")
        self.cancel_btn.pack_forget() # Hide cancel button
        
        self.emp_id_entry.config(state="normal")
        self.emp_id_entry.delete(0, tk.END)
        self.rfid_entry.delete(0, tk.END)
        self.emp_id_entry.focus_set()

    def handle_save(self):
        eid = self.emp_id_entry.get().strip()
        uid = self.rfid_entry.get().strip()

        if not eid or not uid:
            messagebox.showwarning("Input Error", "ID and RFID are required.")
            return

        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    # 1. Check if Teacher exists in main users table
                    cur.execute("SELECT username FROM users WHERE employee_id = %s AND role = 'Teacher'", (eid,))
                    teacher_exists = cur.fetchone()
                    
                    if not teacher_exists:
                        messagebox.showerror("Error", f"Employee ID {eid} is not a registered Teacher.")
                        return

                    # 2. Duplicate check
                    cur.execute("SELECT employee_id FROM teacher_rfid_registration WHERE rfid_uid = %s AND employee_id != %s", (uid, eid))
                    if cur.fetchone():
                        messagebox.showerror("Duplicate RFID", "This card is already assigned to another teacher.")
                        return

                    # 3. Save
                    cur.execute("""
                        INSERT INTO teacher_rfid_registration (employee_id, rfid_uid, status) 
                        VALUES (%s, %s, 'Active') 
                        ON DUPLICATE KEY UPDATE rfid_uid = VALUES(rfid_uid)
                    """, (eid, uid))
                    conn.commit()

            messagebox.showinfo("Success", "Master access granted.")
            self.refresh_list()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT t.employee_id, u.username, t.rfid_uid, t.status 
                        FROM teacher_rfid_registration t
                        JOIN users u ON t.employee_id = u.employee_id
                        ORDER BY u.username ASC
                    """)
                    for row in cur.fetchall():
                        tag = 'active' if row[3] == 'Active' else 'inactive'
                        self.tree.insert("", "end", values=row, tags=(tag,))
            self.tree.tag_configure('active', foreground='green')
            self.tree.tag_configure('inactive', foreground='red')
        except Exception as e:
            print(f"List Refresh Error: {e}")

    def handle_delete(self):
        eid = self.emp_id_entry.get().strip()
        if not eid: return
        
        if messagebox.askyesno("Confirm", "Remove master access?"):
            try:
                with db_connect() as conn:
                    with conn.cursor() as cur:
                        cur.execute("DELETE FROM teacher_rfid_registration WHERE employee_id = %s", (eid,))
                        conn.commit()
                self.refresh_list()
                self.clear_form()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def toggle_status(self, new_status):
        selected = self.tree.focus()
        if not selected: return
        eid = self.tree.item(selected, "values")[0]
        
        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE teacher_rfid_registration SET status = %s WHERE employee_id = %s", (new_status, eid))
                    conn.commit()
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))