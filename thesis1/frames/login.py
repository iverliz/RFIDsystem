import tkinter as tk
from tkinter import messagebox, ttk
from PIL import ImageTk, Image
import os
import sys
import bcrypt
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from utils.database import db_connect

# ================= HELPER FUNCTIONS =================
def add_hover_effect(button, hover_bg, default_bg):
    button.bind("<Enter>", lambda e: button.config(bg=hover_bg))
    button.bind("<Leave>", lambda e: button.config(bg=default_bg))

def get_image_path(target_file):
    """Scan folders once to find the image path"""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for root, dirs, files in os.walk(root_dir):
        if target_file in files:
            return os.path.join(root, target_file)
    return None

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

        target_file = "ccclogo.jpg"
        img_path = get_image_path(target_file)

        if img_path:
            try:
                img = Image.open(img_path).resize((675, 700), Image.Resampling.LANCZOS)
                self.photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(left, image=self.photo, bg="#E0E0E0")
                img_label.image = self.photo 
                img_label.pack(fill=tk.BOTH, expand=True)
            except Exception as e:
                tk.Label(left, text=f"Error: {e}", fg="red").pack(expand=True)
        else:
            tk.Label(left, text=f"COULD NOT FIND: {target_file}", 
                     fg="red", bg="#E0E0E0", font=("Arial", 9)).pack(expand=True)
        
    def login_panel(self):
        panel = tk.Frame(self, width=420, height=550, bg="white", bd=0, highlightthickness=1, highlightbackground="#DDDDDD")
        panel.place(relx=0.78, rely=0.5, anchor="center")
        panel.pack_propagate(False)

        tk.Label(panel, text="Welcome Back!", font=("Helvetica", 24, "bold"),
                 bg="white", fg="#0047AB").pack(pady=(40, 30))

        input_container = tk.Frame(panel, bg="white")
        input_container.pack(fill="x", padx=40)

        tk.Label(input_container, text="Username", bg="white", font=("Arial", 10, "bold")).pack(anchor="w")
        self.username = tk.Entry(input_container, font=("Arial", 12), bg="#F8F9FA", bd=0, highlightthickness=1, highlightbackground="#CCCCCC")
        self.username.pack(fill="x", ipady=8, pady=(5, 15))

        tk.Label(input_container, text="Employee ID", bg="white", font=("Arial", 10, "bold")).pack(anchor="w")
        self.employee_id = tk.Entry(input_container, font=("Arial", 12), bg="#F8F9FA", bd=0, highlightthickness=1, highlightbackground="#CCCCCC")
        self.employee_id.pack(fill="x", ipady=8, pady=(5, 15))

        tk.Label(input_container, text="Password", bg="white", font=("Arial", 10, "bold")).pack(anchor="w")
        pass_frame = tk.Frame(input_container, bg="#F8F9FA", highlightthickness=1, highlightbackground="#CCCCCC")
        pass_frame.pack(fill="x", pady=(5, 0))
        
        self.password = tk.Entry(pass_frame, font=("Arial", 12), bg="#F8F9FA", bd=0, show="*")
        self.password.pack(side=tk.LEFT, fill="x", expand=True, ipady=8, padx=5)

        toggle_button = tk.Button(pass_frame, text="👁️", bg="#F8F9FA", bd=0, cursor="hand2",
                                  command=self.password_visibility)
        toggle_button.pack(side=tk.RIGHT, padx=5)

        btn = tk.Button(panel, text="LOGIN", bg="#0047AB", fg="white", cursor="hand2",
                        font=("Arial", 12, "bold"), bd=0, command=self.login)
        btn.pack(fill="x", padx=40, pady=(30, 10), ipady=10)
        add_hover_effect(btn, "#003380", "#0047AB")

        footer_frame = tk.Frame(panel, bg="white")
        footer_frame.pack(fill="x", padx=40)

        su = tk.Button(footer_frame, text="Create Account", font=("Arial", 9), bg="white", fg="#00A86B",
                        bd=0, cursor="hand2", command=lambda: self.controller.show_frame("SignUpFrame"))
        su.pack(side=tk.LEFT)
        
        forgot_btn = tk.Button(footer_frame, text="Forgot Password?", fg="#666666", bg="white",
                       bd=0, font=("Arial", 9), cursor="hand2",
                       command=lambda: self.controller.show_frame("ForgotPasswordFrame"))
        forgot_btn.pack(side=tk.RIGHT)

    def login(self):
        user = self.username.get().strip()
        emp_id = self.employee_id.get().strip()
        pw = self.password.get()

        if not user or not pw or not emp_id:
            messagebox.showerror("Error", "All fields required")
            return

        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT password, employee_id, role FROM users WHERE username=%s", (user,))
                    result = cur.fetchone()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")
            return

        if result:
            stored_pw, stored_emp_id, role = result
            if emp_id != str(stored_emp_id):
                messagebox.showerror("Error", "Employee ID is incorrect")
            elif not bcrypt.checkpw(pw.encode(), stored_pw.encode()):
                messagebox.showerror("Error", "Password is incorrect")
            else:
                user_data = {"username": user, "employee_id": emp_id, "role": role}
                messagebox.showinfo("Success", f"Login Successful! Welcome {role}")
                self.controller.login_success(user_data)
        else:
            messagebox.showerror("Error", "Username not found")

    def password_visibility(self):
        if self.password.cget("show") == "*":
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

        target_file = "ccclogo.jpg"
        img_path = get_image_path(target_file)

        if img_path:
            try:
                img = Image.open(img_path).resize((675, 700), Image.Resampling.LANCZOS)
                self.photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(left, image=self.photo, bg="#E0E0E0")
                img_label.image = self.photo 
                img_label.pack(fill=tk.BOTH, expand=True)
            except Exception as e:
                tk.Label(left, text=f"Error: {e}", fg="red").pack(expand=True)
        else:
            tk.Label(left, text=f"COULD NOT FIND: {target_file}", 
                     fg="red", bg="#E0E0E0", font=("Arial", 9)).pack(expand=True)

    def signup_panel(self):
        panel = tk.Frame(self, width=420, height=650, bg="white", bd=0, highlightthickness=1, highlightbackground="#DDDDDD")
        panel.place(relx=0.78, rely=0.5, anchor="center")
        panel.pack_propagate(False)

        tk.Label(panel, text="Join Us", font=("Helvetica", 24, "bold"),
                 bg="white", fg="#0047AB").pack(pady=(20, 10))

        form_container = tk.Frame(panel, bg="white")
        form_container.pack(fill="x", padx=40)

        self.username = self.entry(form_container, "Username")
        self.employee_id = self.entry(form_container, "Employee ID")
        
        # --- Password Field ---
        tk.Label(form_container, text="Password", bg="white", font=("Arial", 9, "bold")).pack(anchor="w")
        pass_frame = tk.Frame(form_container, bg="#F8F9FA", highlightthickness=1, highlightbackground="#CCCCCC")
        pass_frame.pack(fill="x", pady=(2, 10))

        self.password = tk.Entry(pass_frame, font=("Arial", 12), bg="#F8F9FA", bd=0, show="*")
        self.password.pack(side=tk.LEFT, expand=True, fill="x", ipady=6, padx=5)

        self.toggle_pass = tk.Button(pass_frame, text="👁️", bg="#F8F9FA", bd=0, cursor="hand2",
                             command=lambda: self.toggle_visibility(self.password))
        self.toggle_pass.pack(side=tk.RIGHT, padx=5)

        # --- Confirm Password Field ---
        tk.Label(form_container, text="Confirm Password", bg="white", font=("Arial", 9, "bold")).pack(anchor="w")
        conf_frame = tk.Frame(form_container, bg="#F8F9FA", highlightthickness=1, highlightbackground="#CCCCCC")
        conf_frame.pack(fill="x", pady=(2, 10))

        self.confirm = tk.Entry(conf_frame, font=("Arial", 12), bg="#F8F9FA", bd=0, show="*")
        self.confirm.pack(side=tk.LEFT, expand=True, fill="x", ipady=6, padx=5)

        self.toggle_conf = tk.Button(conf_frame, text="👁️", bg="#F8F9FA", bd=0, cursor="hand2",
                             command=lambda: self.toggle_visibility(self.confirm))
        self.toggle_conf.pack(side=tk.RIGHT, padx=5)
                           
        # ROLE SELECTION DROPDOWN
        tk.Label(form_container, text="Account Role", bg="white", font=("Arial", 9, "bold")).pack(anchor="w")
        self.role_var = tk.StringVar(value="Teacher")
        self.role_dropdown = ttk.Combobox(form_container, textvariable=self.role_var, state="readonly", font=("Arial", 11))
        self.role_dropdown['values'] = ("Teacher", "Admin")
        self.role_dropdown.pack(fill="x", pady=(2, 10))

        req_frame = tk.Frame(form_container, bg="white")
        req_frame.pack(fill="x", pady=5)
        
        self.pw_reqs = {
            "length": tk.Label(req_frame, text="• 8+ characters", fg="red", bg="white", font=("Arial", 8)),
            "upper": tk.Label(req_frame, text="• Uppercase letter", fg="red", bg="white", font=("Arial", 8)),
            "digit": tk.Label(req_frame, text="• Number", fg="red", bg="white", font=("Arial", 8)),
            "special": tk.Label(req_frame, text="• Special character", fg="red", bg="white", font=("Arial", 8))
        }

        self.pw_reqs["length"].grid(row=0, column=0, sticky="w", padx=5)
        self.pw_reqs["upper"].grid(row=0, column=1, sticky="w", padx=5)
        self.pw_reqs["digit"].grid(row=1, column=0, sticky="w", padx=5)
        self.pw_reqs["special"].grid(row=1, column=1, sticky="w", padx=5)

        self.password.bind("<KeyRelease>", self.validate_password)

        btn_signup = tk.Button(panel, text="CREATE ACCOUNT", bg="#00A86B", fg="white", cursor="hand2",
                        font=("Arial", 12, "bold"), bd=0, command=self.signup)
        btn_signup.pack(fill="x", padx=40, pady=(15, 10), ipady=10)
        add_hover_effect(btn_signup, "#007A4D", "#00A86B")

        back = tk.Button(panel, text="Already have an account? Login", bg="white", fg="#666666",
                         bd=0, font=("Arial", 9), cursor="hand2",
                         command=lambda: self.controller.show_frame("LoginFrame"))
        back.pack()

    def entry(self, panel, text, hide=False):
        tk.Label(panel, text=text, bg="white", font=("Arial", 9, "bold")).pack(anchor="w")
        e = tk.Entry(panel, font=("Arial", 12), bg="#F8F9FA", bd=0, highlightthickness=1, highlightbackground="#CCCCCC", show="*" if hide else "")
        e.pack(fill="x", ipady=6, pady=(2, 10))
        return e

    def toggle_visibility(self, entry_widget):
        if entry_widget.cget("show") == "*":
            entry_widget.config(show="")
        else:
            entry_widget.config(show="*")

    def validate_password(self, event=None):
        pw = self.password.get()
        self.pw_reqs["length"].config(fg="green" if len(pw) >= 8 else "red")
        self.pw_reqs["upper"].config(fg="green" if re.search(r'[A-Z]', pw) else "red")
        self.pw_reqs["digit"].config(fg="green" if re.search(r'\d', pw) else "red")
        self.pw_reqs["special"].config(fg="green" if re.search(r'[\W_]', pw) else "red")

    def signup(self):
        user, emp_id, pw, cpw, role = (self.username.get().strip(), 
                                       self.employee_id.get().strip(), 
                                       self.password.get(), 
                                       self.confirm.get(),
                                       self.role_var.get())

        if not user or not pw or not emp_id:
            messagebox.showerror("Error", "All fields required")
            return
        if pw != cpw:
            messagebox.showerror("Error", "Passwords do not match")
            return
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[\W_]).{8,}$', pw):
            messagebox.showerror("Error", "Password too weak")
            return

        hashed = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM users WHERE employee_id=%s", (emp_id,))
                    if cur.fetchone():
                        messagebox.showerror("Error", "Employee ID exists")
                        return
                    cur.execute("INSERT INTO users (username, password, employee_id, role) VALUES (%s, %s, %s, %s)",
                                (user, hashed, emp_id, role))
                    conn.commit()
            messagebox.showinfo("Success", f"Account created as {role}")
            self.controller.show_frame("LoginFrame")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

# ================= FORGOT PASSWORD FRAME =================
class ForgotPasswordFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#F5F5F5")
        self.controller = controller
        self.forgot_panel()
        
    def forgot_panel(self):
        panel = tk.Frame(self, width=420, height=480, bg="white", bd=0, highlightthickness=1, highlightbackground="#DDDDDD")
        panel.place(relx=0.5, rely=0.5, anchor="center") 
        panel.pack_propagate(False)

        tk.Label(panel, text="Reset Password", font=("Helvetica", 20, "bold"), 
                 bg="white", fg="#0047AB").pack(pady=30)

        container = tk.Frame(panel, bg="white")
        container.pack(fill="x", padx=40)

        tk.Label(container, text="Username", bg="white", font=("Arial", 9, "bold")).pack(anchor="w")
        self.username = tk.Entry(container, font=("Arial", 12), bg="#F8F9FA", bd=0, highlightthickness=1, highlightbackground="#CCCCCC")
        self.username.pack(fill="x", ipady=8, pady=(2, 15))

        tk.Label(container, text="Employee ID", bg="white", font=("Arial", 9, "bold")).pack(anchor="w")
        self.employee_id = tk.Entry(container, font=("Arial", 12), bg="#F8F9FA", bd=0, highlightthickness=1, highlightbackground="#CCCCCC")
        self.employee_id.pack(fill="x", ipady=8, pady=(2, 15))

        tk.Label(container, text="New Password", bg="white", font=("Arial", 9, "bold")).pack(anchor="w")
        self.new_pw = tk.Entry(container, font=("Arial", 12), bg="#F8F9FA", bd=0, highlightthickness=1, highlightbackground="#CCCCCC", show="*")
        self.new_pw.pack(fill="x", ipady=8, pady=(2, 15))

        btn = tk.Button(panel, text="UPDATE PASSWORD", bg="#0047AB", fg="white", cursor="hand2",
                        font=("Arial", 11, "bold"), bd=0, command=self.reset_password)
        btn.pack(fill="x", padx=40, pady=20, ipady=10)

        back = tk.Button(panel, text="Cancel", bg="white", fg="#666666", bd=0, cursor="hand2",
                         command=lambda: self.controller.show_frame("LoginFrame"))
        back.pack()

    def reset_password(self):
        user, emp_id, new_pw = self.username.get().strip(), self.employee_id.get().strip(), self.new_pw.get()

        if not user or not emp_id or not new_pw:
            messagebox.showerror("Error", "Please fill all fields")
            return

        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[\W_]).{8,}$', new_pw):
            messagebox.showerror("Error", "New password is too weak!")
            return

        hashed = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt()).decode()
        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM users WHERE username=%s AND employee_id=%s", (user, emp_id))
                    if cur.fetchone():
                        cur.execute("UPDATE users SET password=%s WHERE username=%s AND employee_id=%s", 
                                    (hashed, user, emp_id))
                        conn.commit()
                        messagebox.showinfo("Success", "Password updated!")
                        self.controller.show_frame("LoginFrame")
                    else:
                        messagebox.showerror("Error", "User details do not match.")
        except Exception as e: 
            messagebox.showerror("Error", f"Database error: {e}")