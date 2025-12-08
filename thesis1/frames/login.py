import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import os

# Helper function to add hover effect on buttons
def add_hover_effect(button, hover_bg, default_bg):
    def on_enter(e):
        button['bg'] = hover_bg
    def on_leave(e):
        button['bg'] = default_bg
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)

# ------------------------ LOGIN FRAME ------------------------
class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F5F5F5")

        # ---------------- LEFT IMAGE ----------------
        self.image_left = tk.Frame(self, width=675, height=700, bg="#E0E0E0")
        self.image_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.image_left.pack_propagate(False)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_dir, "..", "assets", "icon", "ccclogo.jpg")
        image_path = os.path.normpath(image_path)
        try:
            image = Image.open(image_path)
            image = image.resize((675, 700))
            self.photo = ImageTk.PhotoImage(image)
            label = tk.Label(self.image_left, image=self.photo, bg="#E0E0E0")
            label.pack(fill=tk.BOTH, expand=True)
        except FileNotFoundError:
            tk.Label(self.image_left, text="Image not found", bg="gray", fg="white").pack(fill=tk.BOTH, expand=True)

        # ---------------- LOGIN PANEL ----------------
        panel_width = 400
        panel_height = 450
        self.login_frame = tk.Frame(self, width=panel_width, height=panel_height, bg="white", bd=2, relief="groove")
        self.login_frame.place(x=675 + (675 - panel_width)//2, y=(700 - panel_height)//2)
        self.login_frame.pack_propagate(False)

        title = tk.Label(self.login_frame, text="Welcome Back!", font=("Arial", 24, "bold"), bg="white", fg="#0047AB")
        title.place(x=20, y=20)

        tk.Label(self.login_frame, text="Username", font=("Arial", 14), bg="white", fg="#333333").place(x=20, y=80)
        self.username_entry = tk.Entry(self.login_frame, font=("Arial", 14), bg="#F0F0F0", bd=0)
        self.username_entry.place(x=20, y=110, width=250, height=35)

        tk.Label(self.login_frame, text="Password", font=("Arial", 14), bg="white", fg="#333333").place(x=20, y=160)
        self.password_entry = tk.Entry(self.login_frame, font=("Arial", 14), bg="#F0F0F0", bd=0, show="*")
        self.password_entry.place(x=20, y=190, width=250, height=35)

        # Buttons with hover
        self.login_button = tk.Button(self.login_frame, text="Login", font=("Arial", 14, "bold"),
                                      bg="#0047AB", fg="white", bd=0, activebackground="#003380",
                                      command=self.login)
        self.login_button.place(x=20, y=250, width=250, height=45)
        add_hover_effect(self.login_button, "#003380", "#0047AB")

        self.sign_up_button = tk.Button(self.login_frame, text="Sign Up", font=("Arial", 12, "bold"),
                                        bg="#00A86B", fg="white", bd=0, activebackground="#007A4D",
                                        command=lambda: controller.show_frame("SignUpFrame"))
        self.sign_up_button.place(x=20, y=310, width=120, height=35)
        add_hover_effect(self.sign_up_button, "#007A4D", "#00A86B")

        self.forgot_password_button = tk.Button(self.login_frame, text="Forgot Password", font=("Arial", 12),
                                                bg="white", fg="#0047AB", bd=0, activebackground="#F0F0F0",
                                                command=self.forgot_password)
        self.forgot_password_button.place(x=150, y=310, width=120, height=35)
        add_hover_effect(self.forgot_password_button, "#E0E0E0", "white")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        messagebox.showinfo("Login Info", f"Username: {username}\nPassword: {password}")

    def forgot_password(self):
        messagebox.showinfo("Forgot Password", "Forgot Password clicked!")

# ------------------------ SIGN UP FRAME ------------------------
class SignUpFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F5F5F5")

        # ---------------- LEFT IMAGE ----------------
        self.image_left = tk.Frame(self, width=675, height=700, bg="#E0E0E0")
        self.image_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.image_left.pack_propagate(False)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_dir, "..", "assets", "icon", "ccclogo.jpg")
        image_path = os.path.normpath(image_path)
        try:
            image = Image.open(image_path)
            image = image.resize((675, 700))
            self.photo = ImageTk.PhotoImage(image)
            label = tk.Label(self.image_left, image=self.photo, bg="#E0E0E0")
            label.pack(fill=tk.BOTH, expand=True)
        except FileNotFoundError:
            tk.Label(self.image_left, text="Image not found", bg="gray", fg="white").pack(fill=tk.BOTH, expand=True)

        # ---------------- RIGHT FORM PANEL ----------------
        panel_width = 400
        panel_height = 500
        self.form_frame = tk.Frame(self, width=panel_width, height=panel_height, bg="white", bd=2, relief="groove")
        self.form_frame.place(x=675 + (675 - panel_width)//2, y=(700 - panel_height)//2)
        self.form_frame.pack_propagate(False)

        title = tk.Label(self.form_frame, text="Create Account", font=("Arial", 24, "bold"), bg="white", fg="#0047AB")
        title.place(x=20, y=20)

        tk.Label(self.form_frame, text="Username", font=("Arial", 14), bg="white", fg="#333333").place(x=20, y=80)
        self.username_entry = tk.Entry(self.form_frame, font=("Arial", 14), bg="#F0F0F0", bd=0)
        self.username_entry.place(x=20, y=110, width=250, height=35)

        tk.Label(self.form_frame, text="Password", font=("Arial", 14), bg="white", fg="#333333").place(x=20, y=160)
        self.password_entry = tk.Entry(self.form_frame, font=("Arial", 14), bg="#F0F0F0", bd=0, show="*")
        self.password_entry.place(x=20, y=190, width=250, height=35)

        tk.Label(self.form_frame, text="Confirm Password", font=("Arial", 14), bg="white", fg="#333333").place(x=20, y=240)
        self.confirm_password_entry = tk.Entry(self.form_frame, font=("Arial", 14), bg="#F0F0F0", bd=0, show="*")
        self.confirm_password_entry.place(x=20, y=270, width=250, height=35)

        # Buttons with hover
        self.sign_up_button = tk.Button(self.form_frame, text="Sign Up", font=("Arial", 14, "bold"),
                                        bg="#00A86B", fg="white", bd=0, activebackground="#007A4D",
                                        command=self.sign_up)
        self.sign_up_button.place(x=20, y=330, width=250, height=45)
        add_hover_effect(self.sign_up_button, "#007A4D", "#00A86B")

        self.back_button = tk.Button(self.form_frame, text="Back to Login", font=("Arial", 12),
                                     bg="white", fg="#0047AB", bd=0,
                                     command=lambda: controller.show_frame("LoginFrame"))
        self.back_button.place(x=20, y=390, width=250, height=35)
        add_hover_effect(self.back_button, "#E0E0E0", "white")

    def sign_up(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        messagebox.showinfo("Sign Up Info", f"Username: {username}\nPassword: {password}")

# ------------------------ CONTROLLER ------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RFID MANAGEMENT SYSTEM")
        self.geometry("1350x700+0+0")
        self.configure(bg="#F5F5F5")

        self.frames = {}
        container = tk.Frame(self, bg="#F5F5F5")
        container.pack(fill="both", expand=True)

        for F in (LoginFrame, SignUpFrame):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.show_frame("LoginFrame")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()


if __name__ == "__main__":
    app = App()
    app.mainloop()
