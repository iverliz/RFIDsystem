import tkinter as tk
from tkinter import messagebox
from utils.database import db_connect
from utils.security import hash_password  # must return a string
from utils.validators import is_strong_password

class ChangePasswordWindow(tk.Toplevel):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.parent = parent

        # Ensure user_data has at least 3 elements
        if len(user_data) < 3:
            messagebox.showerror("Error", "Invalid user data passed.")
            self.destroy()
            return

        self.employee_id = user_data[1]
        self.username = user_data[2]

        self.title(f"Security Update: ID {self.employee_id}")
        self.geometry("380x300")
        self.configure(padx=20, pady=20)
        self.resizable(False, False)
        self.grab_set()  # Focus on this window

        tk.Label(
            self, text=f"Update Password for ID: {self.employee_id}", 
            font=("Arial", 12, "bold")
        ).pack(pady=(0, 20))

        # Password Fields
        self.new_pass = self.create_input("New Password:")
        self.confirm_pass = self.create_input("Confirm New Password:")

        # Show password toggle
        self.show_var = tk.BooleanVar()
        tk.Checkbutton(
            self, text="Show Passwords", variable=self.show_var, 
            command=self.toggle_pass
        ).pack(anchor="w", pady=(0, 15))

        self.update_btn = tk.Button(
            self, text="UPDATE PASSWORD", bg="#4CAF50", fg="white", 
            font=("Arial", 10, "bold"), height=2, command=self.save_password
        )
        self.update_btn.pack(fill="x", pady=10)

    def create_input(self, label_text):
        tk.Label(self, text=label_text).pack(anchor="w")
        entry = tk.Entry(self, show="*", font=("Arial", 11))
        entry.pack(fill="x", pady=(0, 10))
        return entry

    def toggle_pass(self):
        char = "" if self.show_var.get() else "*"
        self.new_pass.config(show=char)
        self.confirm_pass.config(show=char)

    def save_password(self):
        new_password = self.new_pass.get().strip()
        confirm_password = self.confirm_pass.get().strip()

        if not new_password or not confirm_password:
            messagebox.showwarning("Input Required", "Please enter and confirm the new password.")
            return

        # Validate password strength
        if not is_strong_password(new_password):
            messagebox.showerror(
                "Weak Password", 
                "Password must be 8+ characters, including uppercase, "
                "lowercase, a number, and a special character."
            )
            return

        if new_password != confirm_password:
            messagebox.showerror("Mismatch", "Passwords do not match.")
            return

        try:
            # Disable button to prevent double click
            self.update_btn.config(state="disabled")

            # Hash the password
            hashed = hash_password(new_password)

            with db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE users SET password=%s WHERE employee_id=%s",
                        (hashed, self.employee_id)
                    )
                    conn.commit()

            messagebox.showinfo(
                "Success", f"Password for Employee ID '{self.employee_id}' updated."
            )
            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Update failed: {e}")
            self.update_btn.config(state="normal")