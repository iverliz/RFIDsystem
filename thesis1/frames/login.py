import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import os
import sys
import bcrypt
import secrets
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from utils.database import db_connect

SESSION_FILE = "session.txt"


# ================= BUTTON HOVER =================
def add_hover_effect(button, hover_bg, default_bg):
    button.bind("<Enter>", lambda e: button.config(bg=hover_bg))
    button.bind("<Leave>", lambda e: button.config(bg=default_bg))


# ================= LOGIN FRAME =================
class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#F5F5F5")
        self.controller = controller
        self.failed_attempts = 0
        self.left_image()
        self.login_panel()

    def left_image(self):
        left = tk.Frame(self, width=675, height=700, bg="#E0E0E0")
        left.pack(side=tk.LEFT, fill=tk.BOTH)
        left.pack_propagate(False)

        img_path = os.path.join(os.path.dirname(__file__), "assets", "icon", "ccclogo.jpg")
        if os.path.exists(img_path):
            try:
                img = Image.open(img_path).resize((675, 700))
                self.photo = ImageTk.PhotoImage(img)
                tk.Label(left, image=self.photo).pack(fill=tk.BOTH, expand=True)
            except:
                tk.Label(left, text="Image could not be opened").pack(expand=True)
        else:
            tk.Label(left, text="Image not found", font=("Arial", 20)).pack(expand=True)

    def login_panel(self):
        panel = tk.Frame(self, width=400, height=450, bg="white", bd=2, relief="groove")
        panel.place(x=875, y=125)
        panel.pack_propagate(False)

        tk.Label(panel, text="Welcome Back!", font=("Arial", 24, "bold"),
                 bg="white", fg="#0047AB").place(x=20, y=20)

        # ---------------- Username ----------------
        tk.Label(panel, text="Username", bg="white").place(x=20, y=80)
        self.username = tk.Entry(panel, font=("Arial", 14), bg="#F0F0F0", bd=0)
        self.username.place(x=20, y=110, width=250, height=35)

        # ---------------- Employee ID ----------------
        tk.Label(panel, text="Employee ID", bg="white").place(x=20, y=160)
        self.employee_id = tk.Entry(panel, font=("Arial", 14), bg="#F0F0F0", bd=0)
        self.employee_id.place(x=20, y=190, width=250, height=35)

        # ---------------- Password ----------------
        tk.Label(panel, text="Password", bg="white").place(x=20, y=240)
        self.password = tk.Entry(panel, font=("Arial", 14), bg="#F0F0F0", bd=0, show="*")
        self.password.place(x=20, y=270, width=250, height=35)

        toggle_button = tk.Button(panel, text="👁️", fg="black", font=("Arial", 10, "bold"),
                                  command=self.password_visibility)
        toggle_button.place(x=280, y=270, width=50, height=35)

        # ---------------- Buttons ----------------
        btn = tk.Button(panel, text="Login", bg="#0047AB", fg="white",
                        font=("Arial", 14, "bold"), command=self.login)
        btn.place(x=20, y=330, width=250, height=45)
        add_hover_effect(btn, "#003380", "#0047AB")

        su = tk.Button(panel, text="Sign Up", bg="#00A86B", fg="white",
                       command=lambda: self.controller.show_frame("SignUpFrame"))
        su.place(x=20, y=390, width=120, height=35)
        add_hover_effect(su, "#007A4D", "#00A86B")

    def login(self):
        user = self.username.get().strip()
        emp_id = self.employee_id.get().strip()
        pw = self.password.get()

        if not user or not pw or not emp_id:
            messagebox.showerror("Error", "All fields required")
            return

        if self.failed_attempts >= 5:
            messagebox.showerror("Blocked", "Too many failed attempts. Try later.")
            return

        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT password, employee_id FROM users WHERE username=%s", (user,))
                    result = cur.fetchone()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")
            return

        if result:
            stored_pw, stored_emp_id = result
            if emp_id != str(stored_emp_id):
                messagebox.showerror("Error", "Employee ID is incorrect")
            elif not bcrypt.checkpw(pw.encode(), stored_pw.encode()):
                messagebox.showerror("Error", "Password is incorrect")
            else:
                token = secrets.token_hex(16)
                with open(SESSION_FILE, "w") as f:
                    f.write(token)
                messagebox.showinfo("Success", "Login Successful")
                self.failed_attempts = 0
                self.controller.show_frame("MainDashboard")
        else:
            messagebox.showerror("Error", "Username not found")
            self.failed_attempts += 1

    def password_visibility(self):
        if self.password["show"] == "*":
            self.password.config(show="")
        else:
            self.password.config(show="*")


# ================= SIGN UP FRAME =================
class SignUpFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#F5F5F5")
        self.controller = controller
        self.left_image()
        self.signup_panel()

    def left_image(self):
        left = tk.Frame(self, width=675, height=700, bg="#E0E0E0")
        left.pack(side=tk.LEFT, fill=tk.BOTH)
        left.pack_propagate(False)

        img_path = os.path.join(os.path.dirname(__file__), "assets", "icon", "ccclogo.jpg")
        if os.path.exists(img_path):
            try:
                img = Image.open(img_path).resize((675, 700))
                self.photo = ImageTk.PhotoImage(img)
                tk.Label(left, image=self.photo).pack(fill=tk.BOTH, expand=True)
            except:
                tk.Label(left, text="Image could not be opened").pack(expand=True)
        else:
            tk.Label(left, text="Image not found", font=("Arial", 20)).pack(expand=True)

    def signup_panel(self):
        panel = tk.Frame(self, width=400, height=500, bg="white", bd=2, relief="groove")
        panel.place(x=875, y=100)
        panel.pack_propagate(False)

        tk.Label(panel, text="Create Account", font=("Arial", 24, "bold"),
                 bg="white", fg="#0047AB").place(x=20, y=20)

        # Entries
        self.username = self.entry(panel, "Username", 80)
        self.employee_id = self.entry(panel, "Employee ID", 140)
        self.password = self.entry(panel, "Password", 200, hide=True)
        self.confirm = self.entry(panel, "Confirm Password", 260, hide=True)

        # Password requirements checklist
        self.pw_reqs = {
            "length": tk.Label(panel, text="8+ characters", fg="red", bg="white"),
            "upper": tk.Label(panel, text="Uppercase letter", fg="red", bg="white"),
            "lower": tk.Label(panel, text="Lowercase letter", fg="red", bg="white"),
            "digit": tk.Label(panel, text="Number", fg="red", bg="white"),
            "special": tk.Label(panel, text="Special character", fg="red", bg="white")
        }

        y_offset = 235
        for label in self.pw_reqs.values():
            label.place(x=20, y=y_offset)
            y_offset += 18

        self.password.bind("<KeyRelease>", self.validate_password)

        # Toggle buttons
        toggle_pw = tk.Button(panel, text="👁️", fg="black", font=("Arial", 10, "bold"),
                              command=lambda: self.toggle_password(self.password))
        toggle_pw.place(x=280, y=200, width=50, height=35)

        toggle_confirm = tk.Button(panel, text="👁️", fg="black", font=("Arial", 10, "bold"),
                                   command=lambda: self.toggle_password(self.confirm))
        toggle_confirm.place(x=280, y=260, width=50, height=35)

        # Buttons
        btn = tk.Button(panel, text="Sign Up", bg="#00A86B", fg="white",
                        font=("Arial", 14, "bold"), command=self.signup)
        btn.place(x=20, y=330, width=250, height=45)
        add_hover_effect(btn, "#007A4D", "#00A86B")

        back = tk.Button(panel, text="Back to Login", bg="#FF6347", fg="white",
                         command=lambda: self.controller.show_frame("LoginFrame"))
        back.place(x=20, y=390, width=250, height=35)
        add_hover_effect(back, "#CC3E2E", "#FF6347")

    def entry(self, panel, text, y, hide=False):
        tk.Label(panel, text=text, bg="white", font=("Arial", 12)).place(x=20, y=y)
        e = tk.Entry(panel, font=("Arial", 14), bg="#F0F0F0", bd=0, show="*" if hide else "")
        e.place(x=20, y=y + 30, width=250, height=35)
        return e

    def toggle_password(self, entry_widget):
        if entry_widget["show"] == "*":
            entry_widget.config(show="")
        else:
            entry_widget.config(show="*")

    def validate_password(self, event=None):
        pw = self.password.get()
        # Length
        self.pw_reqs["length"].config(fg="green" if len(pw) >= 8 else "red")
        # Uppercase
        self.pw_reqs["upper"].config(fg="green" if re.search(r'[A-Z]', pw) else "red")
        # Lowercase
        self.pw_reqs["lower"].config(fg="green" if re.search(r'[a-z]', pw) else "red")
        # Digit
        self.pw_reqs["digit"].config(fg="green" if re.search(r'\d', pw) else "red")
        # Special
        self.pw_reqs["special"].config(fg="green" if re.search(r'[\W_]', pw) else "red")

    def signup(self):
        user = self.username.get().strip()
        emp_id = self.employee_id.get().strip()
        pw = self.password.get()
        cpw = self.confirm.get()

        if not user or not pw or not emp_id:
            messagebox.showerror("Error", "All fields required")
            return

        if pw != cpw:
            messagebox.showerror("Error", "Passwords do not match")
            return

        # Password validation
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[\W_]).{8,}$', pw):
            messagebox.showerror("Error", "Password does not meet all requirements")
            return

        hashed = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    # Only check employee_id uniqueness
                    cur.execute("SELECT * FROM users WHERE employee_id=%s", (emp_id,))
                    if cur.fetchone():
                        messagebox.showerror("Error", "Employee ID already exists")
                        return

                    # Insert user (username can duplicate)
                    cur.execute(
                        "INSERT INTO users (username, password, employee_id) VALUES (%s, %s, %s)",
                        (user, hashed, emp_id)
                    )
                    conn.commit()

            messagebox.showinfo("Success", "Account created")
            self.controller.show_frame("LoginFrame")

        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")
