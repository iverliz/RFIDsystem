import tkinter as tk
from tkinter import ttk
from datetime import datetime


def mask_name(name):
    """Mask full name except first letter of each part"""
    if not name:
        return ""
    parts = name.split()
    return " ".join(p[0] + "*" * (len(p) - 1) for p in parts)


class RFIDHistory(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("RFID History (Privacy Mode)")
        self.geometry("900x450")

        tk.Label(
            self,
            text="RFID Tap History (Privacy Protected)",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        columns = ("Fetcher", "Student", "Date", "Time", "Location")

        self.table = ttk.Treeview(self, columns=columns, show="headings")

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, anchor="center", width=160)

        self.table.pack(expand=True, fill="both", padx=10, pady=10)

        # Sample data (privacy ON)
        self.rfid_tap("Maria Santos", "Juan Dela Cruz", "Gate A")
        self.rfid_tap("Jose Reyes", "Ana Cruz", "Gate B")

    def rfid_tap(self, fetcher, student, location, privacy=True):
        now = datetime.now()

        if privacy:
            fetcher = mask_name(fetcher)
            student = mask_name(student)

        self.table.insert(
            "",
            "end",
            values=(
                fetcher,
                student,
                now.strftime("%Y-%m-%d"),
                now.strftime("%I:%M:%S %p"),
                location
            )
        )



