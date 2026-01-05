import tkinter as tk
from tkinter import ttk
from datetime import datetime

def mask_name(name):
    parts = name.split()
    return " ".join(p[0] + "*" * (len(p) - 1) for p in parts)

root = tk.Tk()
root.title("RFID History (Privacy Mode)")
root.geometry("800x400")

tk.Label(root, text="RFID Tap History (Privacy Protected)",
         font=("Arial", 16, "bold")).pack(pady=10)

columns = ("Fetcher", "Student", "Date", "Time", "Location")
table = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    table.heading(col, text=col)
    table.column(col, anchor="center", width=150)

table.pack(expand=True, fill="both")

def rfid_tap(fetcher, student, location, privacy=True):
    now = datetime.now()

    if privacy:
        fetcher = mask_name(fetcher)
        student = mask_name(student)

    table.insert(
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

# Example taps (privacy ON)
rfid_tap("Maria Santos", "Juan Dela Cruz", "Gate A")
rfid_tap("Jose Reyes", "Ana Cruz", "Gate B")

root.mainloop()
