import tkinter as tk
from tkinter import ttk
from datetime import datetime


def mask_name(name):
    """Mask full name except first letter of each part"""
    if not name:
        return ""
    parts = name.split()
    return " ".join(p[0] + "*" * (len(p) - 1) for p in parts)


class RFIDHistory(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#b2e5ed")
        self.controller = controller

        # ================= TITLE =================
        tk.Label(
            self,
            text="RFID Tap History (Privacy Protected)",
            font=("Arial", 18, "bold"),
            bg="#b2e5ed"
        ).pack(pady=15)

        # ================= TABLE =================
        columns = ("Fetcher", "Student", "Date", "Time", "Location")

        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(expand=True, fill="both", padx=20, pady=10)

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, anchor="center", width=160)

        self.table.pack(expand=True, fill="both", padx=10, pady=10)

        # ================= SAMPLE DATA =================
        self.rfid_tap("Maria Santos", "Juan Dela Cruz", "Gate A")
        self.rfid_tap("Jose Reyes", "Ana Cruz", "Gate B")

    # ================= FUNCTIONS =================
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
