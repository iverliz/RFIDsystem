import tkinter as tk
from tkinter import ttk
from datetime import datetime

# Main window
root = tk.Tk()
root.title("RFID Student History Log")
root.geometry("800x400")

# Title
title = tk.Label(root, text="Student RFID Tap History", font=("Arial", 16, "bold"))
title.pack(pady=10)

# Table (Treeview)
columns = ("Fetcher", "Student", "Date", "Time", "Location")
table = ttk.Treeview(root, columns=columns, show="headings")

# Column headings
for col in columns:
    table.heading(col, text=col)
    table.column(col, anchor="center", width=150)

table.pack(expand=True, fill="both", padx=10, pady=10)

# Function to simulate RFID tap
def rfid_tap(fetcher, student, location):
    now = datetime.now()
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

# SAMPLE RFID TAPS (simulation)
rfid_tap("Maria Santos", "Juan Dela Cruz", "Gate A")
rfid_tap("Maria Santos", "Juan Dela Cruz", "Gate B")
rfid_tap("Jose Reyes", "Ana Cruz", "Gate A")

root.mainloop()
