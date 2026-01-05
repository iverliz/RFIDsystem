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

        frame = MainDashboard(self)
        self.frames["MainDashboard"] = frame
        frame.place(relwidth=1, relheight=1)

        self.show_frame("MainDashboard")

    def show_frame(self, name):
        self.frames[name].tkraise()

    def logout(self):
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        self.destroy()
        App().mainloop()


def start_app():
    if os.path.exists(SESSION_FILE):
        app = Rfid()
        app.mainloop()
    else:
        App().mainloop()


if __name__ == "__main__":
    start_app()
