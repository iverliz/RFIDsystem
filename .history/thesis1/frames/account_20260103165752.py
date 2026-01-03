import tkinter as tk
from tkinter import messagebox, ttk


class Account(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#b2e5ed")
        self.controller = controller

        # ================= SEARCH BAR =================
        self.search_var = tk.StringVar()

        self.search_entry = tk.Entry(
            self,
            textvariable=self.search_var,
            width=30,
            font=("Arial", 15),
            fg="gray"
        )
        self.search_entry.place(x=20, y=20)
        self.search_entry.insert(0, "Search account")

        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<FocusOut>", self.add_placeholder)

        tk.Button(
            self,
            text="🔍",
            font=("Arial", 14),
            command=self.search_account
        ).place(x=260, y=20)

        # ================= TABLE =================
        table_frame = tk.Frame(self, bg="white")
        table_frame.place(x=20, y=80, width=900, height=550)

        columns = ("id", "username", "role")
        self.account_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=20
        )

        self.account_table.heading("id", text="ID")
        self.account_table.heading("username", text="Username")
        self.account_table.heading("role", text="Role")

        self.account_table.column("id", width=80)
        self.account_table.column("username", width=300)
        self.account_table.column("role", width=150)

        self.account_table.pack(fill="both", expand=True, padx=10, pady=10)

        # SAMPLE DATA (replace with database later)
        self.load_sample_accounts()

        # ================= ACTION BUTTONS =================
        btn_frame = tk.Frame(self, bg="#b2e5ed")
        btn_frame.place(x=950, y=150)

        tk.Button(
            btn_frame,
            text="CHANGE PASSWORD",
            width=20,
            height=2,
            bg="#2196F3",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.change_password
        ).pack(pady=10)

        tk.Button(
            btn_frame,
            text="DELETE ACCOUNT",
            width=20,
            height=2,
            bg="#F44336",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.delete_account
        ).pack(pady=10)

    # ================= FUNCTIONS =================
    def clear_placeholder(self, event):
        if self.search_entry.get() == "Search account":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="black")

    def add_placeholder(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search account")
            self.search_entry.config(fg="gray")

    def load_sample_accounts(self):
        data = [
            (1, "admin", "Admin"),
            (2, "john_doe", "User"),
            (3, "rfid_staff", "User")
        ]
        for row in data:
            self.account_table.insert("", "end", values=row)

    def search_account(self):
        keyword = self.search_var.get().lower()
        for item in self.account_table.get_children():
            values = self.account_table.item(item, "values")
            if keyword in str(values).lower():
                self.account_table.selection_set(item)
                self.account_table.see(item)
                return
        messagebox.showinfo("Search", "Account not found")

    def change_password(self):
        selected = self.account_table.focus()
        if not selected:
            messagebox.showwarning("Select", "Select an account first")
            return

        ChangePasswordWindow(self)

    def delete_account(self):
        selected = self.account_table.focus()
        if not selected:
            messagebox.showwarning("Select", "Select an account first")
            return

        if messagebox.askyesno("Delete Account", "Are you sure you want to delete this account?"):
            self.account_table.delete(selected)
            messagebox.showinfo("Deleted", "Account deleted successfully")


# ================= CHANGE PASSWORD POPUP =================
class ChangePasswordWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Change Password")
        self.geometry("350x250")
        self.resizable(False, False)
        self.grab_set()  # modal window

        tk.Label(self, text="New Password", font=("Arial", 12)).pack(pady=10)
        self.new_pass = tk.Entry(self, show="*", width=30)
        self.new_pass.pack()

        tk.Label(self, text="Confirm Password", font=("Arial", 12)).pack(pady=10)
        self.confirm_pass = tk.Entry(self, show="*", width=30)
        self.confirm_pass.pack()

        tk.Button(
            self,
            text="Save",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            width=15,
            command=self.save_password
        ).pack(pady=20)

    def save_password(self):
        if self.new_pass.get() != self.confirm_pass.get():
            messagebox.showerror("Error", "Passwords do not match")
            return

        messagebox.showinfo("Success", "Password changed successfully")
        self.destroy()
