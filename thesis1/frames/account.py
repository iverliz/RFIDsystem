import tkinter as tk
from tkinter import messagebox, ttk
import os
import sys
import bcrypt
from datetime import datetime
import re 
# =================== PATH SETUP ===================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from utils.database import db_connect

# =================== SECURITY UTILS ===================
def hash_password(password: str) -> str:
    """Hash password using bcrypt with a high work factor."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()

def check_password(password: str, hashed: str) -> bool:
    """Verify a plain password against a stored hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())

# =================== MAIN ACCOUNT CLASS ===================
class Account(tk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent, bg="#b2e5ed")
        self.controller = controller
        
        # Header Section
        header = tk.Frame(self, bg="#0047AB", height=90)
        header.pack(fill="x")
        tk.Label(header, text="USER MANAGEMENT",
                 font=("Arial", 22, "bold"), bg="#0047AB", fg="white").pack(side="left", padx=30, pady=25)

        # Content Container
        content = tk.Frame(self, bg="#b2e5ed")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=0) # Buttons don't need to stretch
        content.rowconfigure(1, weight=1)

        # Search Bar Area
        search_frame = tk.Frame(content, bg="#b2e5ed")
        search_frame.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=35, font=("Arial", 12))
        self.search_entry.pack(side="left", padx=(0, 5), ipady=3)
        
        tk.Button(search_frame, text="Search User", bg="#0047AB", fg="white", 
                  command=self.search_account).pack(side="left")
        tk.Button(search_frame, text="Refresh", command=self.load_accounts).pack(side="left", padx=5)

        # Account Table
        table_frame = tk.Frame(content, bg="white", bd=1, relief="solid")
        table_frame.grid(row=1, column=0, sticky="nsew")
        
        columns = ("id","employee_id" ,"username", "created", "role")
        self.account_table = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Table Styling
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        
        col_config = {"id": (60, "center"), "employee_id": (100, "center"), "username": (250, "w"), "created": (180, "center"), "role": (120, "center")}
        for col, (width, anchor) in col_config.items():
            self.account_table.heading(col, text=col.upper())
            self.account_table.column(col, width=width, anchor=anchor)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.account_table.yview)
        self.account_table.configure(yscrollcommand=scrollbar.set)
        self.account_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Sidebar Buttons
        btn_frame = tk.Frame(content, bg="#b2e5ed")
        btn_frame.grid(row=1, column=1, sticky="n", padx=(20, 0))
        
        button_specs = [
            ("CHANGE PASSWORD", "#2196F3", self.change_password),
            ("DELETE ACCOUNT", "#F44336", self.delete_account)
        ]
        
        for text, color, cmd in button_specs:
            tk.Button(btn_frame, text=text, width=18, height=2, bg=color, fg="white",
                      font=("Arial", 10, "bold"), command=cmd).pack(pady=5)

        self.load_accounts()

    # ================= LOGIC =================
    def load_accounts(self):
        """Fetch all users from DB safely."""
        self.account_table.delete(*self.account_table.get_children())
        try:
            with db_connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, employee_id, username, created_at, 'Administrator' FROM users ORDER BY id DESC")
                for row in cursor.fetchall():
                    self.account_table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load accounts: {e}")

    def search_account(self):
        query = self.search_var.get().strip()
        if not query:
            self.load_accounts()
            return

        self.account_table.delete(*self.account_table.get_children())
        try:
            with db_connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, employee_id, username, created_at, 'Administrator' FROM users WHERE username LIKE %s", (f"%{query}%",))
                for row in cursor.fetchall():
                    self.account_table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Search Error", str(e))

    def change_password(self):
        selected = self.account_table.focus()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an account to modify.")
            return
        ChangePasswordWindow(self, self.account_table.item(selected, "values"))

    def delete_account(self):
        selected = self.account_table.focus()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an account to delete.")
            return
        
        user_data = self.account_table.item(selected, "values")
        user_id, username = user_data[0], user_data[1]

        # Prevent self-deletion if info is available in controller
        if hasattr(self.controller, 'current_user') and username == self.controller.current_user:
            messagebox.showerror("Action Denied", "You cannot delete your own account while logged in.")
            return

        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete account: {username}?\nThis action cannot be undone."):
            try:
                with db_connect() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
                    conn.commit()
                messagebox.showinfo("Success", "Account removed successfully.")
                self.load_accounts()
            except Exception as e:
                messagebox.showerror("Database Error", str(e))

# ================= SECURE PASSWORD MODAL =================
class ChangePasswordWindow(tk.Toplevel):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.parent = parent
        # Assuming user_data now passes (employee_id, username)
        self.employee_id = user_data[0] 
        self.username = user_data[1]
        
        self.title(f"Security Update: ID {self.employee_id}")
        self.geometry("380x300")
        self.configure(padx=20, pady=20)
        self.resizable(False, False)
        self.grab_set() 

        # Changed label to show Employee ID
        tk.Label(self, text=f"Update Password for ID: {self.employee_id}", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))

        # Password Fields
        self.new_pass = self.create_input("New Password:")
        self.confirm_pass = self.create_input("Confirm New Password:")

        # Show password toggle
        self.show_var = tk.BooleanVar()
        tk.Checkbutton(self, text="Show Passwords", variable=self.show_var, 
                       command=self.toggle_pass).pack(anchor="w")

        tk.Button(self, text="UPDATE PASSWORD", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                  height=2, command=self.save_password).pack(fill="x", pady=20)

    def create_input(self, label_text):
        tk.Label(self, text=label_text).pack(anchor="w")
        entry = tk.Entry(self, show="*", font=("Arial", 11))
        entry.pack(fill="x", pady=(0, 15))
        return entry

    def toggle_pass(self):
        char = "" if self.show_var.get() else "*"
        self.new_pass.config(show=char)
        self.confirm_pass.config(show=char)

    def save_password(self):
        new_password = self.new_pass.get()
        confirm_password = self.confirm_pass.get()

        # Regex for your specific password policy (8+ chars, Upper, Lower, Digit, Special)
        password_regex = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[\W_]).{8,}$'

        if not re.match(password_regex, new_password):
            messagebox.showerror("Weak Password", 
                                 "Password must be 8+ characters, including uppercase, "
                                 "lowercase, a number, and a special character.")
            return
            
        if new_password != confirm_password:
            messagebox.showerror("Mismatch", "Passwords do not match.")
            return

        try:
            # Using bcrypt as per your previous code
            hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
            
            with db_connect() as conn:
                with conn.cursor() as cursor:
                    # CHANGED: Update WHERE clause to use employee_id
                    cursor.execute("UPDATE users SET password=%s WHERE employee_id=%s", 
                                   (hashed, self.employee_id))
                    conn.commit()
                    
            messagebox.showinfo("Success", f"Password for Employee ID '{self.employee_id}' updated.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Update failed: {e}")