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

        tk.Label(
            self,
            text="EXPORT SYSTEM RECORDS",
            font=("Arial", 26, "bold"),
            bg="#b2e5ed",
            fg="#0047AB"
        ).pack(pady=40)

        tk.Button(
            self,
            text="EXPORT REPORT",
            font=("Arial", 14, "bold"),
            width=20,
            height=2,
            bg="#4CAF50",
            fg="white",
            command=self.open_export_window
        ).pack()

    # ================= EXPORT POPUP =================
    def open_export_window(self):
        win = tk.Toplevel(self)
        win.title("Choose Export Type")
        win.geometry("350x250")
        win.resizable(False, False)

        export_type = tk.StringVar(value="students")

        tk.Label(
            win, text="Select data to export",
            font=("Arial", 16, "bold")
        ).pack(pady=15)

        tk.Radiobutton(win, text="Students", variable=export_type,
                       value="students", font=("Arial", 12)).pack(anchor="w", padx=40)

        tk.Radiobutton(win, text="Teachers", variable=export_type,
                       value="teachers", font=("Arial", 12)).pack(anchor="w", padx=40)

        tk.Radiobutton(win, text="Fetchers", variable=export_type,
                       value="fetchers", font=("Arial", 12)).pack(anchor="w", padx=40)

        tk.Button(
            win, text="Export",
            width=15,
            font=("Arial", 12, "bold"),
            bg="#2196F3",
            fg="white",
            command=lambda: self.export_data(export_type.get(), win)
        ).pack(pady=20)

    # ================= EXPORT LOGIC =================
    def export_data(self, export_type, window):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )
        if not file_path:
            return

        # SAMPLE DATA (replace with MySQL later)
        if export_type == "students":
            headers = ["Student ID", "Full Name", "Grade"]
            rows = [
                ("2023001", "Juan Dela Cruz", "Grade 10"),
                ("2023002", "Maria Santos", "Grade 9"),
            ]

        elif export_type == "teachers":
            headers = ["Teacher ID", "Name", "Subject"]
            rows = [
                ("T001", "Mr. Reyes", "Math"),
                ("T002", "Ms. Cruz", "English"),
            ]

        else:  # fetchers
            headers = ["Fetcher RFID", "Name", "Contact"]
            rows = [
                ("RF123", "Pedro Dela Cruz", "09123456789"),
                ("RF124", "Ana Santos", "09987654321"),
            ]

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(rows)

            window.destroy()
            messagebox.showinfo("Success", f"{export_type.title()} exported successfully")

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = Report(root)
    root.mainloop()
