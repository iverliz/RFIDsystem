import tkinter as tk
from tkinter import messagebox


class RfidRegistration(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg="#b2e5ed")
        self.root = root

        root.title("RFID MANAGEMENT SYSTEM - RFID REGISTRATION")
        root.geometry("1350x700+0+0")

        self.pack(fill="both", expand=True)

        # ================= SEARCH BAR =================
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            self,
            textvariable=self.search_var,
            width=30,
            font=("Arial", 15),
            fg="gray"
        )
        self.search_entry.place(x=20, y=20)
        self.search_entry.insert(0, "Search")
        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<FocusOut>", self.add_placeholder)

        tk.Button(self, text="🔍", command=self.search).place(x=260, y=20)

        # ================= FETCHER FRAME (LEFT) =================
        self.fetcher_frame = tk.Frame(
            self, width=500, height=500,
            bg="white", bd=2, relief="groove"
        )
        self.fetcher_frame.place(x=30, y=100)
        self.fetcher_frame.pack_propagate(False)

        tk.Label(
            self.fetcher_frame,
            text="FETCHER INFORMATION",
            font=("Arial", 24, "bold"),
            bg="white", fg="#0047AB"
        ).place(x=20, y=20)

        # RFID
        tk.Label(self.fetcher_frame, text="RFID:", font=("Arial", 14), bg="white").place(x=20, y=80)
        self.rfid_var = tk.StringVar()
        self.rfid_entry = tk.Entry(self.fetcher_frame, textvariable=self.rfid_var, font=("Arial", 14), width=30)
        self.rfid_entry.place(x=90, y=80)
        self.rfid_entry.bind("<Return>", self.on_rfid_scanned)
        self.rfid_entry.focus()

        # Name
        tk.Label(self.fetcher_frame, text="Name:", font=("Arial", 14), bg="white").place(x=20, y=120)
        self.name_var = tk.StringVar()
        tk.Entry(self.fetcher_frame, textvariable=self.name_var, font=("Arial", 14), width=30).place(x=90, y=120)

        # Address
        tk.Label(self.fetcher_frame, text="Address:", font=("Arial", 14), bg="white").place(x=20, y=160)
        self.address_var = tk.StringVar()
        tk.Entry(self.fetcher_frame, textvariable=self.address_var, font=("Arial", 14), width=30).place(x=140, y=160)

        # Contact
        tk.Label(self.fetcher_frame, text="Contact Number:", font=("Arial", 14), bg="white").place(x=20, y=200)
        self.contact_var = tk.StringVar()
        tk.Entry(self.fetcher_frame, textvariable=self.contact_var, font=("Arial", 14), width=30).place(x=170, y=200)

        # ================= STUDENT FRAME (RIGHT) =================
        self.student_frame = tk.Frame(
            self, width=600, height=500,
            bg="white", bd=2, relief="groove"
        )
        self.student_frame.place(x=650, y=100)
        self.student_frame.pack_propagate(False)

        tk.Label(
            self.student_frame,
            text="STUDENT INFORMATION",
            font=("Arial", 24, "bold"),
            bg="white", fg="#0047AB"
        ).place(x=20, y=20)

        # Student ID
        tk.Label(self.student_frame, text="Student ID:", font=("Arial", 14), bg="white").place(x=20, y=80)
        self.student_id_var = tk.StringVar()
        tk.Entry(self.student_frame, textvariable=self.student_id_var, font=("Arial", 14), width=30).place(x=160, y=80)

        # Student Name
        tk.Label(self.student_frame, text="Name:", font=("Arial", 14), bg="white").place(x=20, y=120)
        self.student_name_var = tk.StringVar()
        tk.Entry(self.student_frame, textvariable=self.student_name_var, font=("Arial", 14), width=30).place(x=160, y=120)

        # Grade
        tk.Label(self.student_frame, text="Grade:", font=("Arial", 14), bg="white").place(x=20, y=160)
        self.grade_var = tk.StringVar()
        tk.Entry(self.student_frame, textvariable=self.grade_var, font=("Arial", 14), width=30).place(x=160, y=160)

        # Fetcher Name
        tk.Label(self.student_frame, text="Fetcher Name:", font=("Arial", 14), bg="white").place(x=20, y=200)
        self.fetcher_name_var = tk.StringVar()
        tk.Entry(self.student_frame, textvariable=self.fetcher_name_var, font=("Arial", 14), width=30).place(x=160, y=200)

        # Teacher
        tk.Label(self.student_frame, text="Teacher:", font=("Arial", 14), bg="white").place(x=20, y=240)
        self.teacher_var = tk.StringVar()
        tk.Entry(self.student_frame, textvariable=self.teacher_var, font=("Arial", 14), width=30).place(x=160, y=240)
             
                # ================= BUTTONS =================
btn_y = 630

        tk.Button(
    self,
    text="ADD",
    font=("Arial", 14, "bold"),
    bg="#4CAF50",
    fg="white",
    width=12,
    command=self.add_record
).place(x=450, y=btn_y)

tk.Button(
    self,
    text="EDIT",
    font=("Arial", 14, "bold"),
    bg="#2196F3",
    fg="white",
    width=12,
    command=self.edit_record
).place(x=600, y=btn_y)

tk.Button(
    self,
    text="DELETE",
    font=("Arial", 14, "bold"),
    bg="#F44336",
    fg="white",
    width=12,
    command=self.delete_record
).place(x=750, y=btn_y)



    # ================= RFID FUNCTION =================
    def on_rfid_scanned(self, event):
        tag = self.rfid_var.get().strip()
        if tag:
            messagebox.showinfo("RFID Scanned", f"Tag ID: {tag}")
            self.rfid_var.set("")
            self.rfid_entry.focus()

    # ================= SEARCH =================
    def clear_placeholder(self, event):
        if self.search_entry.get() == "Search":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="black")

    def add_placeholder(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search")
            self.search_entry.config(fg="gray")

    def search(self):
        print("Searching:", self.search_var.get())


if __name__ == "__main__":
    root = tk.Tk()
    app = RfidRegistration(root)
    root.mainloop()
