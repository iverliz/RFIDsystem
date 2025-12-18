import tkinter as tk
from tkinter import messagebox, filedialog
import csv


class Report(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg="#b2e5ed")
        self.root = root

        root.title("RFID MANAGEMENT SYSTEM - REPORT")
        root.geometry("1350x700+0+0")
        self.pack(fill="both", expand=True)

        # ================= HEADER =================
        header = tk.Label(
            self,
            text="SYSTEM REPORT SUMMARY",
            font=("Arial", 26, "bold"),
            bg="#b2e5ed",
            fg="#0047AB"
        )
        header.pack(pady=20)

        # ================= COUNTER FRAME =================
        counter_frame = tk.Frame(self, bg="#b2e5ed")
        counter_frame.pack(pady=20)

        self.student_count = tk.StringVar(value="0")
        self.teacher_count = tk.StringVar(value="0")
        self.fetcher_count = tk.StringVar(value="0")

        self.create_counter(counter_frame, "STUDENTS", self.student_count, "#4CAF50", 0)
        self.create_counter(counter_frame, "TEACHERS", self.teacher_count, "#2196F3", 1)
        self.create_counter(counter_frame, "FETCHERS", self.fetcher_count, "#FF9800", 2)

        # ================= REPORT FRAME =================
        self.report_frame = tk.Frame(
            self, width=500, height=280,
            bg="white", bd=2, relief="groove"
        )
        self.report_frame.pack(pady=30)
        self.report_frame.pack_propagate(False)

        tk.Label(
            self.report_frame,
            text="EXPORT REPORTS",
            font=("Arial", 20, "bold"),
            bg="white",
            fg="#0047AB"
        ).pack(pady=20)

        tk.Button(
            self.report_frame,
            text="EXPORT TO CSV",
            width=20,
            height=2,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            command=self.export_csv
        ).pack(pady=30)

        # TEMP SAMPLE COUNTS (replace with DB later)
        self.load_counts()

    # ================= COUNTER BOX =================
    def create_counter(self, parent, title, var, color, col):
        box = tk.Frame(
            parent, width=220, height=120,
            bg="white", bd=2, relief="groove"
        )
        box.grid(row=0, column=col, padx=20)
        box.pack_propagate(False)

        tk.Label(
            box, text=title,
            font=("Arial", 14, "bold"),
            bg="white"
        ).pack(pady=10)

        tk.Label(
            box, textvariable=var,
            font=("Arial", 28, "bold"),
            bg="white",
            fg=color
        ).pack()

    # ================= LOAD COUNTS =================
    def load_counts(self):
        # 🔧 SAMPLE VALUES (replace with MySQL queries)
        self.student_count.set("120")
        self.teacher_count.set("15")
        self.fetcher_count.set("98")

    # ================= EXPORT CSV =================
    def export_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if not file_path:
            return

        try:
            data = [
                ("Category", "Total"),
                ("Students", self.student_count.get()),
                ("Teachers", self.teacher_count.get()),
                ("Fetchers", self.fetcher_count.get()),
            ]

            with open(file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerows(data)

            messagebox.showinfo("Success", "Report exported successfully")

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = Report(root)
    root.mainloop()
