import tkinter as tk
from tkinter import ttk, messagebox


class RfidRegistration(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg="#b2e5ed")
        self.root = root

        root.title("RFID MANAGEMENT SYSTEM - RFID REGISTRATION")
        root.geometry("1350x700+0+0")

        self.pack(fill="both", expand=True)

        # ================= SEARCH BAR =================
        self.search_var = tk.StringVar()

        search_frame = tk.Frame(self, bg="#b2e5ed")
        search_frame.pack(pady=10)

        tk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side="left", padx=5)
        tk.Button(search_frame, text="Search", command=self.search).pack(side="left")

        # ================= FETCHER INFORMATION =================
        self.fetcher_frame = tk.Frame(self, width=400, height=500, bg="white", bd=2, relief="groove")
        self.fetcher_frame.place(x=50, y=120)
        self.fetcher_frame.pack_propagate(False)

        tk.Label(self.fetcher_frame, text="FETCHER INFORMATION",
                 font=("Arial", 18, "bold"), bg="white", fg="#0047AB").pack(pady=10)

        self.fetcher_name = self.create_label(self.fetcher_frame, "Name:")
        self.fetcher_rfid = self.create_label(self.fetcher_frame, "RFID:")
        self.fetcher_address = self.create_label(self.fetcher_frame, "Address:")
        self.fetcher_phone = self.create_label(self.fetcher_frame, "Phone Number:")

        # ================= STUDENT INFORMATION =================
        self.student_frame = tk.Frame(self, width=400, height=500, bg="white", bd=2, relief="groove")
        self.student_frame.place(x=500, y=120)
        self.student_frame.pack_propagate(False)

        tk.Label(self.student_frame, text="STUDENT INFORMATION",
                 font=("Arial", 18, "bold"), bg="white", fg="#0047AB").pack(pady=10)

        self.student_name = self.create_label(self.student_frame, "Name:")
        self.student_id = self.create_label(self.student_frame, "Student ID:")
        self.student_grade = self.create_label(self.student_frame, "Grade:")
        self.student_fetcher = self.create_label(self.student_frame, "Fetcher:")

        # ================= BUTTONS =================
        button_frame = tk.Frame(self, bg="#b2e5ed")
        button_frame.place(x=950, y=150)

        tk.Button(button_frame, text="Add", width=15, command=self.add).pack(pady=10)
        tk.Button(button_frame, text="Edit", width=15, command=self.edit).pack(pady=10)
        tk.Button(button_frame, text="Delete", width=15, command=self.delete).pack(pady=10)

        # ================= TABLE =================
        table_frame = tk.Frame(self)
        table_frame.place(x=50, y=650)

        self.tree = ttk.Treeview(
            self,
            columns=("RFID", "Name", "Address", "Phone"),
            show="headings",
            height=8
        )

        self.tree.heading("RFID", text="RFID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Address", text="Address")
        self.tree.heading("Phone", text="Phone Number")

        self.tree.column("RFID", width=120)
        self.tree.column("Name", width=200)
        self.tree.column("Address", width=250)
        self.tree.column("Phone", width=150)

        self.tree.pack(side="bottom", pady=10)

    # ================= HELPER =================
    def create_label(self, parent, text):
        tk.Label(parent, text=text, bg="white").pack()
        lbl = tk.Label(parent, text="", bg="white", fg="black")
        lbl.pack(pady=3)
        return lbl

    # ================= FUNCTIONS =================
    def search(self):
        keyword = self.search_var.get()
        messagebox.showinfo("Search", f"Searching for: {keyword}")

    def add(self):
        messagebox.showinfo("Add", "Add button clicked")

    def edit(self):
        messagebox.showinfo("Edit", "Edit button clicked")

    def delete(self):
        messagebox.showinfo("Delete", "Delete button clicked")


if __name__ == "__main__":
    root = tk.Tk()
    app = RfidRegistration(root)
    root.mainloop()
