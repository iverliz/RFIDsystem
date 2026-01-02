import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import os
import hashlib
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.database import db_connect


# ================= BUTTON HOVER =================
def add_hover_effect(button, hover_bg, default_bg):
    button.bind("<Enter>", lambda e: button.config(bg=hover_bg))
    button.bind("<Leave>", lambda e: button.config(bg=default_bg))


# ================= LOGIN FRAME =================
class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#F5F5F5")
        self.controller = controller

        self.left_image()
        self.login_panel()

    def left_image(self):
        left = tk.Frame(self, width=675, height=700, bg="#E0E0E0")
        left.pack(side=tk.LEFT)
        left.pack_propagate(False)

        img_path = os.path.join(os.path.dirname(__file__), "assets", "icon", "ccclogo.jpg")
        try:
            img = Image.open(img_path).resize((675, 700))
            self.photo = ImageTk.PhotoImage(img)
            tk.Label(left, image=self.photo).pack(fill=tk.BOTH, expand=True)
        except:
            tk.Label(left, text="Image not found").pack()

    def login_panel(self):
        panel = tk.Frame(self, width=400, height=450, bg="white", bd=2, relief="groove")
        panel.place(x=875, y=125)
        panel.pack_propagate(False)

        tk.Label(panel, text="Welcome Back!", font=("Arial", 24, "bold"),
                 bg="white", fg="#0047AB").place(x=20, y=20)

        tk.Label(panel, text="Username", bg="white").place(x=20, y=90)
        self.username = tk.Entry(panel, font=("Arial", 14), bg="#F0F0F0", bd=0)
        self.username.place(x=20, y=120, width=250, height=35)

        tk.Label(panel, text="Password", bg="white").place(x=20, y=170)
        self.password = tk.Entry(panel, font=("Arial", 14),
                                 bg="#F0F0F0", bd=0, show="*")
        self.password.place(x=20, y=200, width=250, height=35)

        btn = tk.Button(panel, text="Login", bg="#0047AB", fg="white",
                        font=("Arial", 14, "bold"), command=self.login)
        btn.place(x=20, y=260, width=250, height=45)
        add_hover_effect(btn, "#003380", "#0047AB")

        su = tk.Button(panel, text="Sign Up", bg="#00A86B", fg="white",
                       command=lambda: self.controller.show_frame("SignUpFrame"))
        su.place(x=20, y=320, width=120, height=35)
        add_hover_effect(su, "#007A4D", "#00A86B")

    def login(self):
        user = self.username.get()
        pw = self.password.get()

        if not user or not pw:
            messagebox.showerror("Error", "All fields required")
            return

        hashed = hashlib.sha256(pw.encode()).hexdigest()

        conn = db_connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (user, hashed)
        )
        result = cur.fetchone()
        conn.close()

        if result:
            messagebox.showinfo("Success", "Login Successful")
            # open dashboard here
        else:
            messagebox.showerror("Error", "Invalid login")


# ================= SIGN UP FRAME =================
class SignUpFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#F5F5F5")
        self.controller = controller

        self.left_image()
        self.signup_panel()

    def left_image(self):
        left = tk.Frame(self, width=675, height=700, bg="#E0E0E0")
        left.pack(side=tk.LEFT)
        left.pack_propagate(False)


        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.append(BASE_DIR)

                
        img_path = os.path.join(os.path.dirname(__file__), "assets", "icon", "ccclogo.jpg")
        try:
            img = Image.open(img_path).resize((675, 700))
            self.photo = ImageTk.PhotoImage(img)
            tk.Label(left, image=self.photo).pack(fill=tk.BOTH, expand=True)
        except:
            tk.Label(left, text="Image not found").pack()

    def signup_panel(self):
        panel = tk.Frame(self, width=400, height=500, bg="white", bd=2, relief="groove")
        panel.place(x=875, y=100)
        panel.pack_propagate(False)

        tk.Label(panel, text="Create Account", font=("Arial", 24, "bold"),
                 bg="white", fg="#0047AB").place(x=20, y=20)

        self.username = self.entry(panel, "Username", 90)
        self.password = self.entry(panel, "Password", 170, True)
        self.confirm = self.entry(panel, "Confirm Password", 250, True)

        btn = tk.Button(panel, text="Sign Up", bg="#00A86B", fg="white",
                        font=("Arial", 14, "bold"), command=self.signup)
        btn.place(x=20, y=330, width=250, height=45)
        add_hover_effect(btn, "#007A4D", "#00A86B")

        back = tk.Button(panel, text="Back to Login",
                         command=lambda: self.controller.show_frame("LoginFrame"))
        back.place(x=20, y=390, width=250, height=35)

    def entry(self, panel, text, y, hide=False):
        tk.Label(panel, text=text, bg="white").place(x=20, y=y)
        e = tk.Entry(panel, font=("Arial", 14), bg="#F0F0F0",
                     bd=0, show="*" if hide else "")
        e.place(x=20, y=y+30, width=250, height=35)
        return e

    def signup(self):
        user = self.username.get()
        pw = self.password.get()
        cpw = self.confirm.get()

        if not user or not pw:
            messagebox.showerror("Error", "All fields required")
            return

        if pw != cpw:
            messagebox.showerror("Error", "Passwords do not match")
            return

        hashed = hashlib.sha256(pw.encode()).hexdigest()

        try:
            conn = db_connect()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s,%s)",
                (user, hashed)
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Account created")
            self.controller.show_frame("LoginFrame")

        except:
            messagebox.showerror("Error", "Username already exists")


# ================= APP CONTROLLER =================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RFID MANAGEMENT SYSTEM")
        self.geometry("1350x700+0+0")

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (LoginFrame, SignUpFrame):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("LoginFrame")

    def show_frame(self, name):
        self.frames[name].tkraise()


if __name__ == "__main__":
    App().mainloop()
