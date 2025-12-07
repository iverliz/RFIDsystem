import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image

class Login(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.parent.title("Login Page")
        self.parent.geometry("400x300")  # Set window size
        self.pack(fill="both", expand=True)

        # Title
        title = tk.Label(self, text="Login Page", font=("Arial", 20))
        title.pack(pady=20)

        # Login box frame
        self.login_box = tk.Frame(
            self, width=400, height=250,
            bg="white",
            highlightbackground="black",
            highlightthickness=1.5
        )
        self.login_box.place(relx=0.5, rely=0.5, anchor="w")
        self.login_box.pack_propagate(False)

        self.image_left = tk.Frame (
            self, width=400, height=250
        )
        self.image_left.place(relx=0.5, rely=0.5, anchor="e")
        self.image_left.pack_propagate(False)
        image = Image.open("assets/icon/ccclogo.jpg")
        image = image.resize((600, 400))
        photo = ImageTk.PhotoImage(image)
        label = tk.Label(self.image_left, image=photo)
        label.image = photo
        label.place(x=0, y=0)


        # Username label and entry
        tk.Label(self.login_box, text="Username", font=("Arial", 12)).place(x=50, y=30)
        self.username_entry = tk.Entry(self.login_box, width=30)
        self.username_entry.place(x=150, y=30)

        # Password label and entry
        tk.Label(self.login_box, text="Password", font=("Arial", 12)).place(x=50, y=70)
        self.password_entry = tk.Entry(self.login_box, width=30, show="*")
        self.password_entry.place(x=150, y=70)

        # Forgot password label
        tk.Label(self.login_box, text="Forgot Password?", font=("Arial", 10), fg="blue").place(x=150, y=110)

        # Buttons
        login_button = tk.Button(self.login_box, text="Login", width=15, command=self.login)
        login_button.place(x=50, y=150)

        signup_button = tk.Button(self.login_box, text="Sign Up", width=15, command=self.sign_up)
        signup_button.place(x=200, y=150)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        # Add your login logic here (e.g., MySQL check)
        messagebox.showinfo("Login Info", f"Username: {username}\nPassword: {password}")

    def sign_up(self):
        messagebox.showinfo("Sign Up", "Sign Up button clicked!")


if __name__ == "__main__":
    root = tk.Tk()
    app = Login(root)
    root.mainloop()
