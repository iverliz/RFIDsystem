import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import csv
import os
import sys

from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt

# ================= DATABASE =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from utils.database import db_connect


class Report(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#b2e5ed")
        self.controller = controller
        self.pack(fill="both", expand=True)

        # ================= HEADER =================
        header = tk.Frame(self, bg="#0047AB", height=65)
        header.pack(fill="x")

        tk.Label(
            header,
            text="DATE-BASED REPORTS",
            font=("Arial", 20, "bold"),
            bg="#0047AB",
            fg="white"
        ).pack(side="left", padx=20, pady=15)

        # ================= MAIN =================
        content = tk.Frame(self, bg="#b2e5ed")
        content.pack(fill="both", expand=True, padx=10, pady=5)
        content.columnconfigure((0, 1), weight=1)

        # ================= FILTER =================
        filter_card = tk.Frame(content, bg="white", bd=2, relief="groove")
        filter_card.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)

        tk.Label(filter_card, text="From:", bg="white").grid(row=0, column=0, padx=5, pady=5)
        self.from_date = tk.Entry(filter_card, width=12)
        self.from_date.grid(row=0, column=1)
        self.from_date.insert(0, "2024-01-01")

        tk.Label(filter_card, text="To:", bg="white").grid(row=0, column=2, padx=5)
        self.to_date = tk.Entry(filter_card, width=12)
        self.to_date.grid(row=0, column=3)
        self.to_date.insert(0, datetime.today().strftime("%Y-%m-%d"))

        tk.Button(
            filter_card,
            text="Apply",
            bg="#2196F3",
            fg="white",
            width=10,
            command=self.apply_filter
        ).grid(row=0, column=4, padx=8)

        # ================= TABLES =================
        tables = tk.Frame(content, bg="#b2e5ed")
        tables.grid(row=1, column=0, columnspan=2, sticky="nsew")
        tables.columnconfigure((0, 1), weight=1)

        self.student_table = self.create_table(
            tables, "STUDENTS",
            ["ID", "Name", "Grade", "Date"], 0, 0
        )

        self.teacher_table = self.create_table(
            tables, "TEACHERS",
            ["ID", "Name", "Date"], 0, 1
        )

        self.fetcher_table = self.create_table(
            tables, "FETCHERS",
            ["ID", "Fetcher", "Contact", "Date"], 1, 0, colspan=2
        )

        # ================= BUTTONS =================
        btn_frame = tk.Frame(self, bg="#b2e5ed")
        btn_frame.pack(pady=5)

        tk.Button(
            btn_frame,
            text="EXPORT",
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            width=14,
            command=self.export_popup
        ).grid(row=0, column=0, padx=8)

        tk.Button(
            btn_frame,
            text="SHOW CHART",
            font=("Arial", 11, "bold"),
            bg="#FF9800",
            fg="white",
            width=14,
            command=self.show_chart
        ).grid(row=0, column=1, padx=8)

        self.apply_filter()

    # ================= TABLE CREATOR =================
    def create_table(self, parent, title, columns, r, c, colspan=1):
        frame = tk.Frame(parent, bg="white", bd=2, relief="groove")
        frame.grid(row=r, column=c, columnspan=colspan, padx=6, pady=6, sticky="nsew")

        tk.Label(
            frame,
            text=title,
            font=("Arial", 14, "bold"),
            bg="white"
        ).pack(pady=2)

        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=5   # 🔥 KEY FIX
        )
        tree.pack(side="left", fill="both", expand=True, padx=5)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=130, anchor="center")

        tree.count_var = tk.StringVar(value="Total: 0")
        tk.Label(
            frame,
            textvariable=tree.count_var,
            bg="white",
            fg="#0047AB",
            font=("Arial", 10, "bold")
        ).pack(pady=2)

        return tree

    # ================= DATABASE =================
    def fetch_data(self, query):
        conn = db_connect()
        cur = conn.cursor()
        cur.execute(query)
        data = cur.fetchall()
        conn.close()
        return data

    def get_students(self):
        return self.fetch_data("SELECT ID, Student_name, grade_lvl, created_at FROM student")

    def get_teachers(self):
        return self.fetch_data("SELECT ID, Teacher_name, created_at FROM teacher")

    def get_fetchers(self):
        return self.fetch_data("SELECT ID, fetcher_name, contact, created_at FROM fetcher")

    # ================= FILTER =================
    def apply_filter(self):
        for t in (self.student_table, self.teacher_table, self.fetcher_table):
            t.delete(*t.get_children())

        f = datetime.strptime(self.from_date.get(), "%Y-%m-%d").date()
        t = datetime.strptime(self.to_date.get(), "%Y-%m-%d").date()

        self.fill(self.student_table, self.get_students(), f, t)
        self.fill(self.teacher_table, self.get_teachers(), f, t)
        self.fill(self.fetcher_table, self.get_fetchers(), f, t)

    def fill(self, table, data, f, t):
        count = 0
        for row in data:
            d = row[-1]
            if isinstance(d, str):
                d = datetime.strptime(d, "%Y-%m-%d").date()
            if f <= d <= t:
                table.insert("", "end", values=row)
                count += 1
        table.count_var.set(f"Total: {count}")

    # ================= EXPORT =================
    def export_popup(self):
        win = tk.Toplevel(self)
        win.title("Export")
        win.geometry("280x240")
        win.resizable(False, False)

        choice = tk.StringVar(value="students")
        fmt = tk.StringVar(value="csv")

        tk.Label(win, text="Choose Data", font=("Arial", 11, "bold")).pack(pady=5)
        for v in ("students", "teachers", "fetchers"):
            tk.Radiobutton(win, text=v.title(), variable=choice, value=v).pack(anchor="w", padx=40)

        tk.Label(win, text="Format", font=("Arial", 11, "bold")).pack(pady=5)
        for v in ("csv", "excel", "pdf"):
            tk.Radiobutton(win, text=v.upper(), variable=fmt, value=v).pack(anchor="w", padx=40)

        tk.Button(
            win,
            text="Export",
            bg="#4CAF50",
            fg="white",
            width=14,
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
                csv.writer(f).writerows([headers] + rows)

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
            y -= 25
            for r in rows:
                if y < 50:
                    pdf.showPage()
                    y = 750
                pdf.drawString(40, y, " | ".join(map(str, r)))
                y -= 18
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
        plt.bar(labels, values)
        plt.title("Total Records")
        plt.ylabel("Count")
        plt.show()
