import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
import os
import sys
import csv

# ================= PATH SETUP =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.database import db_connect

def mask_name(name):
    """Mask full name except first letter of each part (e.g., J*** D*** C***)"""
    if not name:
        return ""
    parts = name.split()
    return " ".join(p[0] + "*" * (len(p) - 1) for p in parts)

class RFIDHistory(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#b2e5ed")
        self.controller = controller

        # ================= HEADER & DASHBOARD =================
        header = tk.Frame(self, bg="#0047AB", height=80)
        header.pack(fill="x")
        
        tk.Label(header, text="RFID LOG HISTORY", font=("Arial", 20, "bold"), 
                 bg="#0047AB", fg="white").pack(side="left", padx=30, pady=20)
        
        self.stats_var = tk.StringVar(value="Today's Taps: 0")
        tk.Label(header, textvariable=self.stats_var, font=("Arial", 12, "bold"), 
                 bg="#0047AB", fg="#FFD700").pack(side="right", padx=30)

        # ================= CONTROL PANEL (Filters) =================
        control_frame = tk.Frame(self, bg="#b2e5ed", padx=20, pady=10)
        control_frame.pack(fill="x")

        tk.Label(control_frame, text="Search Name:", bg="#b2e5ed").pack(side="left")
        self.search_var = tk.StringVar()
        tk.Entry(control_frame, textvariable=self.search_var, width=20).pack(side="left", padx=5)

        tk.Label(control_frame, text="Date (YYYY-MM-DD):", bg="#b2e5ed").pack(side="left", padx=10)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(control_frame, textvariable=self.date_var, width=12).pack(side="left", padx=5)

        tk.Button(control_frame, text="Refresh Data", command=self.load_history, 
                  bg="#2196F3", fg="white").pack(side="left", padx=10)
        
        tk.Button(control_frame, text="Export CSV", command=self.export_to_csv, 
                  bg="#4CAF50", fg="white").pack(side="right", padx=10)

        # ================= TABLE =================
        columns = ("Fetcher", "Student", "Date", "Time", "Location", "Status")
        
        table_container = tk.Frame(self, bg="white", bd=1, relief="solid")
        table_container.pack(expand=True, fill="both", padx=20, pady=10)

        self.table = ttk.Treeview(table_container, columns=columns, show="headings", selectmode="browse")
        
        # Configure Columns
        column_widths = {"Fetcher": 180, "Student": 180, "Date": 100, "Time": 100, "Location": 120, "Status": 100}
        for col in columns:
            self.table.heading(col, text=col.upper())
            self.table.column(col, anchor="center", width=column_widths.get(col, 150))

        # Add Scrollbar
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        
        self.table.pack(side="left", expand=True, fill="both")
        scrollbar.pack(side="right", fill="y")

        # Initial Load
        self.load_history()

    # ================= DATABASE LOGIC =================
    def load_history(self):
        """Fetch and mask history from the attendance_logs table"""
        self.table.delete(*self.table.get_children())
        search_query = self.search_var.get().strip()
        date_query = self.date_var.get().strip()

        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    # Query construction with optional search/date filters
                    sql = """
                        SELECT fetcher_name, student_name, log_date, log_time, location, status 
                        FROM attendance_logs 
                        WHERE log_date = %s
                    """
                    params = [date_query]

                    if search_query:
                        sql += " AND (fetcher_name LIKE %s OR student_name LIKE %s)"
                        params.extend([f"%{search_query}%", f"%{search_query}%"])

                    sql += " ORDER BY log_time DESC"
                    
                    cur.execute(sql, tuple(params))
                    rows = cur.fetchall()

                    for row in rows:
                        # Apply Privacy Masking
                        masked_row = (
                            mask_name(row[0]), # Fetcher
                            mask_name(row[1]), # Student
                            row[2],            # Date
                            row[3],            # Time
                            row[4],            # Location
                            row[5]             # Status
                        )
                        self.table.insert("", "end", values=masked_row)

                    self.stats_var.set(f"Taps on {date_query}: {len(rows)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load history: {e}")

    # ================= UTILITY FUNCTIONS =================
    def export_to_csv(self):
        """Export the CURRENTLY VIEWED table data to a CSV file"""
        if not self.table.get_children():
            messagebox.showwarning("Export", "No data available to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"RFID_Log_{self.date_var.get()}.csv"
        )

        if file_path:
            try:
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Fetcher", "Student", "Date", "Time", "Location", "Status"])
                    for row_id in self.table.get_children():
                        writer.writerow(self.table.item(row_id)["values"])
                messagebox.showinfo("Success", f"Data exported to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))

    def manual_rfid_tap(self, fetcher, student, location, status="Verified"):
        """Function to be called by the RFID scanner listener to log a tap"""
        now = datetime.now()
        log_date = now.strftime("%Y-%m-%d")
        log_time = now.strftime("%I:%M:%S %p")

        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO attendance_logs (fetcher_name, student_name, log_date, log_time, location, status)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (fetcher, student, log_date, log_time, location, status))
                    conn.commit()
            
            # If current view is today, refresh the table
            if self.date_var.get() == log_date:
                self.load_history()
        except Exception as e:
            print(f"Log Error: {e}")