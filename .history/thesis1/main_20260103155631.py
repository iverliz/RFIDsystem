import tkinter as tk
from frames.login import App
from frames.main_dashboard import MainDashboard

import os

SESSION_FILE = "session.txt"


class Rfid(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("RFID MANAGEMENT SYSTEM")
        self.geometry("1350x700+0+0")

        self.frames = {}

        for F in (
            MainDashboard,
            
        ):
            frame = F(self)
            self.frames[F.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        if self.is_logged_in():
            self.show_frame("MainDashboard")
        else:
            self.open_login()

    def show_frame(self, name):
        self.frames[name].tkraise()

    def open_login(self):
        self.destroy()
        app = App()
        app.mainloop()

    def is_logged_in(self):
        return os.path.exists(SESSION_FILE)

    def login_success(self):
        with open(SESSION_FILE, "w") as f:
            f.write("logged_in")
        self.show_frame("MainDashboard")

    def logout(self):
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        self.open_login()


if __name__ == "__main__":
    app = Rfid()
    app.mainloop()
