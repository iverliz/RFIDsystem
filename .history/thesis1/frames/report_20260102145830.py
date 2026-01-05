import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, date
import csv
import os
import sys

# Excel
from openpyxl import Workbook

# PDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Chart
import matplotlib.pyplot as plt

# ================= DATABASE CONNECTION =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.database import db_connect   # ✅ correct import


class Report(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg="#b2e5ed")
        self.root = root

        root.title("RFID MANAGEMENT SYSTEM - REPORT")
        root.geometry("1350x700+0+0")
        self.pack(fill="both", expand=True)

        # ================= TITLE =================
        tk.Label(
            self, text="DATE-BASED REPORTS",
            font=("Arial", 24, "bold"),
            bg="#b2e5ed", fg="#0047AB"
        ).pack(pady=10)

        # ================= DATE FILTER =================
        filter_frame = tk.Frame(self, bg="white", bd=2, relief="groove")
        filter_frame.pack(pady=10, ipadx=10, ipady=10)

        tk.Label(filter_frame, text="From:", bg="white").grid(row=0, column=0)
        self.from_date = tk.Entry(filter_frame)
        self.from_date.grid(row=0, column=1, padx=5)
        self.from_date.insert(0, "2024-01-01")

        tk.Label(filter_frame, text="To:", bg="white").grid(row=0, column=2)
        self.to_date = tk.Entry(filter_frame)
        self.to_date.grid(row=0, column=3, padx=5)
        self.to_date.insert(0, datetime.today().strftime("%Y-%m-%d"))

        tk.Button(
            filter_frame, text="Apply Filter",
            command=self.apply_filter,
            bg="#2196F3", fg="white"
        ).grid(row=0, column=4, padx=10)

        # ================= TABLES =================
        table_frame = tk.Frame(self, bg="#b2e5ed")
        table_frame.pack()

        self.student_table = self.create_table(
            table_frame, "STUDENTS", ["ID ", "Name","Grade Level", "Date"], 0, 0
        )
        self.teacher_table = self.create_table(
            table_frame, "TEACHERS", ["ID", "Name", "Date"], 0, 1
        )
        self.fetcher_table = self.create_table(
            table_frame, "FETCHERS", ["ID", "FETCHER ", "Date"], 1, 0, colspan=2
        )

        # ================= ACTION BUTTONS =================
        btn_frame = tk.Frame(self, bg="#b2e5ed")
        btn_frame.pack(pady=15)

        tk.Button(
            btn_frame, text="EXPORT",
            font=("Arial", 12, "bold"),
            bg="#4CAF50", fg="white",
            width=15,
            command=self.export_popup
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            btn_frame, text="SHOW CHART",
            font=("Arial", 12, "bold"),
            bg="#FF9800", fg="white",
            width=15,
            command=self.show_chart
        ).grid(row=0, column=1, padx=10)

        self.apply_filter()

    # ================= TABLE CREATOR =================
    def create_table(self, parent, title, columns, r, c, colspan=1):
        frame = tk.Frame(parent, bg="white", bd=2, relief="groove")
        frame.grid(row=r, column=c, columnspan=colspan, padx=10, pady=10)

        tk.Label(frame, text=title, font=("Arial", 16, "bold"), bg="white").pack()

        tree = ttk.Treeview(frame, columns=columns, show="headings", height=7)
        tree.pack(padx=10, pady=5)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=160)

        tree.count_var = tk.StringVar(value="Total: 0")
        tk.Label(frame, textvariable=tree.count_var,
                 font=("Arial", 11, "bold"), bg="white", fg="#0047AB").pack()

        return tree

    # ================= DATABASE FETCH =================
    def fetch_data(self, query):
        conn = db_connect()
        cur = conn.cursor()
        cur.execute(query)
        data = cur.fetchall()
        conn.close()
        return data

    def get_students(self):
        return self.fetch_data("SELECT ID, Student_name,grade_lvl, date FROM student")

    def get_teachers(self):
        return self.fetch_data("SELECT ID, Teeacher_name,Teacher_grade, date FROM teacher")

    def get_fetchers(self):
        return self.fetch_data("SELECT ID, fetcher_name, contact, date FROM fetcher")

    # ================= DATE FILTER =================
    def apply_filter(self):
        for table in (self.student_table, self.teacher_table, self.fetcher_table):
            table.delete(*table.get_children())

        f = datetime.strptime(self.from_date.get(), "%Y-%m-%d").date()
        t = datetime.strptime(self.to_date.get(), "%Y-%m-%d").date()

        self.fill(self.student_table, self.get_students(), f, t)
        self.fill(self.teacher_table, self.get_teachers(), f, t)
        self.fill(self.fetcher_table, self.get_fetchers(), f, t)

    def fill(self, table, data, f, t):
        count = 0
        for row in data:
            d = row[-1]
            if isinstance(d, datetime):
                d = d.date()
            elif isinstance(d, str):
                d = datetime.strptime(d, "%Y-%m-%d").date()

            if f <= d <= t:
                table.insert("", "end", values=row)
                count += 1

        table.count_var.set(f"Total: {count}")

    # ================= EXPORT =================
    def export_popup(self):
        win = tk.Toplevel(self)
        win.title("Export")
        win.geometry("300x250")

        choice = tk.StringVar(value="students")
        fmt = tk.StringVar(value="csv")

        tk.Label(win, text="Choose Data").pack(pady=5)
        for v in ("students", "teachers", "fetchers"):
            tk.Radiobutton(win, text=v.title(), variable=choice, value=v).pack()

        tk.Label(win, text="Format").pack(pady=5)
        for v in ("csv", "excel", "pdf"):
            tk.Radiobutton(win, text=v.upper(), variable=fmt, value=v).pack()

        tk.Button(
            win, text="Export", bg="#4CAF50", fg="white",
            command=lambda: self.export(choice.get(), fmt.get(), win)
        ).pack(pady=10)

    def export(self, choice, fmt, win):
        table = {
            "students": self.student_table,
            "teachers": self.teacher_table,
            "fetchers": self.fetcher_table
        }[choice]

        path = filedialog.asksaveasfilename(defaultextension=f".{fmt}")
        if not path:
            return

        headers = table["columns"]
        rows = [table.item(i, "values") for i in table.get_children()]

        if fmt == "csv":
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)

        elif fmt == "excel":
            wb = Workbook()
            ws = wb.active
            ws.append(headers)
            for r in rows:
                ws.append(r)
            wb.save(path)

        elif fmt == "pdf":
            pdf = canvas.Canvas(path, pagesize=letter)
            y = 750
            pdf.drawString(40, y, " | ".join(headers))
            y -= 30
            for r in rows:
                if y < 50:
                    pdf.showPage()
                    y = 750
                pdf.drawString(40, y, " | ".join(map(str, r)))
                y -= 20
            pdf.save()

        win.destroy()
        messagebox.showinfo("Success", "Export completed")

    # ================= CHART =================
    def show_chart(self):
        labels = ["Students", "Teachers", "Fetchers"]
        values = [
            len(self.student_table.get_children()),
            len(self.teacher_table.get_children()),
            len(self.fetcher_table.get_children())
        ]

        plt.bar(labels, values, color=["#2196F3", "#4CAF50", "#FF9800"])
        plt.title("Total Records")
        plt.ylabel("Count")
        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    Report(root)
    root.mainloop()
