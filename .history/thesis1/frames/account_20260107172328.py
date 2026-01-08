import tkinter as tk
from tkinter import messagebox, ttk
import os
import sys
import bcrypt  # <- new

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from utils.database import db_connect

# =================== PASSWORD HASHING ===================
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

def check_password(password: str, hashed: str) -> bool:
    """Verify password against stored hash"""
    return bcrypt.checkpw(password.encode(), hashed.encode())

# =================== ACCOUNT FRAME ===================
class Account(tk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent, bg="#b2e5ed")
        self.controller = controller
        self.pack(fill="both", expand=True)

        # Header
        header = tk.Frame(self, bg="#0047AB", height=90)
        header.pack(fill="x")
        tk.Label(header, text="ACCOUNT INFORMATION",
                 font=("Arial", 24, "bold"), bg="#0047AB", fg="white").pack(side="left", padx=30, pady=25)

        # Content
        content = tk.Frame(self, bg="#b2e5ed")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(1, weight=1)

        # Search Bar
        search_frame = tk.Frame(content, bg="#b2e5ed")
        search_frame.grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30, font=("Arial", 14), fg="gray")
        self.search_entry.pack(side="left", ipady=5)
        self.search_entry.insert(0, "Search account")
        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<FocusOut>", self.add_placeholder)
        tk.Button(search_frame, text="🔍", font=("Arial", 14), command=self.search_account).pack(side="left", padx=5)

        # Account Table
        table_frame = tk.Frame(content, bg="white", bd=2, relief="groove")
        table_frame.grid(row=1, column=0, sticky="nsew")
        columns = ("id", "username", "created")
        self.account_table = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col, w in zip(columns, [80, 300, 200]):
            self.account_table.heading(col, text=col.title())
            self.account_table.column(col, width=w, anchor="center" if col=="id" else "w")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.account_table.yview)
        self.account_table.configure(yscrollcommand=scrollbar.set)
        self.account_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Buttons
        btn_frame = tk.Frame(content, bg="#b2e5ed")
        btn_frame.grid(row=1, column=1, sticky="n", padx=20)
        tk.Button(btn_frame, text="CHANGE PASSWORD", width=20, height=2, bg="#2196F3", fg="white",
                  font=("Arial", 11, "bold"), command=self.change_password).pack(pady=10, fill="x")
        tk.Button(btn_frame, text="DELETE ACCOUNT", width=20, height=2, bg="#F44336", fg="white",
                  font=("Arial", 11, "bold"), command=self.delete_account).pack(pady=10, fill="x")

        self.load_accounts()

    # ================= FUNCTIONS =================
    def clear_placeholder(self, event):
        if self.search_entry.get() == "Search account":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="black")

    def add_placeholder(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search account")
            self.search_entry.config(fg="gray")

    def load_accounts(self):
        self.account_table.delete(*self.account_table.get_children())
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, created_at FROM users")
            for row in cursor.fetchall():
                self.account_table.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def search_account(self):
        keyword = self.search_var.get().lower()
        self.account_table.delete(*self.account_table.get_children())
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, created_at FROM users WHERE LOWER(username) LIKE %s", (f"%{keyword}%",))
            rows = cursor.fetchall()
            for row in rows:
                self.account_table.insert("", "end", values=row)
            conn.close()
            if not rows:
                messagebox.showinfo("Search", "Account not found")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def change_password(self):
        if not self.account_table.focus():
            messagebox.showwarning("Select", "Select an account first")
            return
        ChangePasswordWindow(self)

    def delete_account(self):
        selected = self.account_table.focus()
        if not selected:
            messagebox.showwarning("Select", "Select an account first")
            return
        user_id = self.account_table.item(selected, "values")[0]

        if messagebox.askyesno("Delete", "Delete this account?"):
            try:
                conn = db_connect()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
                conn.commit()
                conn.close()
                self.load_accounts()
                messagebox.showinfo("Deleted", "Account deleted")
            except Exception as e:
                messagebox.showerror("Database Error", str(e))

# ================= CHANGE PASSWORD WINDOW =================
class ChangePasswordWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Change Password")
        self.geometry("350x250")
        self.resizable(False, False)
        self.grab_set()

        self.user_id = parent.account_table.item(parent.account_table.focus(), "values")[0]

        tk.Label(self, text="New Password", font=("Arial", 12)).pack(pady=(20, 5))
        self.new_pass = tk.Entry(self, show="*", width=30)
        self.new_pass.pack()
        tk.Label(self, text="Confirm Password", font=("Arial", 12)).pack(pady=(15, 5))
        self.confirm_pass = tk.Entry(self, show="*", width=30)
        self.confirm_pass.pack()

        tk.Button(self, text="Save", bg="#4CAF50", fg="white", width=15, command=self.save_password).pack(pady=25)

    def save_password(self):
        new_pw = self.new_pass.get()
        confirm_pw = self.confirm_pass.get()

        if new_pw != confirm_pw:
            messagebox.showerror("Error", "Passwords do not match")
            return
        if len(new_pw) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return

        hashed_pw = hash_password(new_pw)

        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password=%s WHERE id=%s", (hashed_pw, self.user_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Password updated securely")
            self.parent.load_accounts()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
