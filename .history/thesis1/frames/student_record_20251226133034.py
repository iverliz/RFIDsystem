import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import ImageTk, Image


class Student(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg="#b2e5ed")
        self.root = root

        root.title("RFID MANAGEMENT SYSTEM - STUDENT RECORD")
        root.geometry("1350x700+0+0")

        self.pack(fill="both", expand=True)

        # ================= HEADER =================
        self.student_frame = tk.Frame(
            self, height=95, bg="#0047AB", bd=2, relief="groove"
        )
        self.student_frame.pack(fill="x")

        tk.Label(
            self.student_frame,
            text="STUDENT INFORMATION",
            font=("Arial", 24, "bold"),
            bg="#0047AB",
            fg="white"
        ).place(x=50, y=25)

        # ================= LEFT BOX =================
        self.student_left = tk.Frame(
            self, width=500, height=550, bg="white", bd=2, relief="groove"
        )
        self.student_left.place(x=50, y=125)
        self.student_left.pack_propagate(False)

        # ================= PHOTO FRAME =================
        self.photo_frame = tk.Frame(
            self.student_left, width=200, height=200,
            bg="#E0E0E0", bd=2, relief="ridge"
        )
        self.photo_frame.place(x=20, y=20)
        self.photo_frame.pack_propagate(False)

        self.photo_label = tk.Label(self.photo_frame, bg="#E0E0E0")
        self.photo_label.pack(fill="both", expand=True)

        tk.Button(
            self.student_left,
            text="Upload Photo",
            width=15,
            command=self.upload_photo
        ).place(x=60, y=240)

        # ================= STUDENT DETAILS =================
        y = 290
        label_font = ("Arial", 12)
        entry_font = ("Arial", 12)

        self.fullname_var = tk.StringVar()
        self.grade_var = tk.StringVar()
        self.student_id_var = tk.StringVar()
        self.guardian_name_var = tk.StringVar()
        self.guardian_contact_var = tk.StringVar()

        fields = [
            ("Full Name:", self.fullname_var),
            ("Grade Level:", self.grade_var),
            ("Student ID:", self.student_id_var),
            ("Guardian Name:", self.guardian_name_var),
            ("Guardian Contact:", self.guardian_contact_var),
            ("Teacher Name> ")
        ]

        for i, (label, var) in enumerate(fields):
            tk.Label(self.student_left, text=label, bg="white",
                     font=label_font).place(x=20, y=y + i * 40)
            tk.Entry(self.student_left, textvariable=var,
                     font=entry_font, width=30).place(x=160, y=y + i * 40)

        # ================= ACTION BUTTONS =================
        tk.Button(
            self.student_left, text="ADD", width=10,
            font=("Arial", 12, "bold"),
            bg="#4CAF50", fg="white",
            command=self.add_student
        ).place(x=40, y=510)

        tk.Button(
            self.student_left, text="EDIT", width=10,
            font=("Arial", 12, "bold"),
            bg="#2196F3", fg="white",
            command=self.edit_student
        ).place(x=180, y=510)

        tk.Button(
            self.student_left, text="DELETE", width=10,
            font=("Arial", 12, "bold"),
            bg="#F44336", fg="white",
            command=self.delete_student
        ).place(x=320, y=510)

        # ================= RIGHT PANEL =================
        self.right_panel = tk.Frame(
            self, width=550, height=500,
            bg="white", bd=2, relief="groove"
        )
        self.right_panel.place(x=700, y=150)
        self.right_panel.pack_propagate(False)

        tk.Label(
            self.right_panel,
            text="Search Student",
            font=("Arial", 16, "bold"),
            bg="white"
        ).place(x=20, y=20)

        self.search_student_var = tk.StringVar()
        tk.Entry(
            self.right_panel,
            textvariable=self.search_student_var,
            font=("Arial", 12),
            width=25
        ).place(x=20, y=60)

        tk.Button(
            self.right_panel,
            text="Search",
            width=10,
            command=self.search_student
        ).place(x=300, y=57)

        self.student_count_var = tk.StringVar(value="Total Students: 0")
        tk.Label(
            self.right_panel,
            textvariable=self.student_count_var,
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#0047AB"
        ).place(x=20, y=100)

        columns = ("id", "name", "grade")
        self.student_table = ttk.Treeview(
            self.right_panel,
            columns=columns,
            show="headings",
            height=12
        )

        for col, text in zip(columns, ["Student ID", "Full Name", "Grade"]):
            self.student_table.heading(col, text=text)
            self.student_table.column(col, width=160)

        self.student_table.place(x=20, y=140, width=500)

    # ================= FUNCTIONS =================
    def upload_photo(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if not file_path:
            return

        img = Image.open(file_path).resize((200, 200))
        self.photo = ImageTk.PhotoImage(img)
        self.photo_label.config(image=self.photo)
        self.photo_label.image = self.photo

    def update_student_count(self):
        count = len(self.student_table.get_children())
        self.student_count_var.set(f"Total Students: {count}")

    def add_student(self):
        self.student_table.insert("", "end", values=(
            self.student_id_var.get(),
            self.fullname_var.get(),
            self.grade_var.get()
        ))
        self.update_student_count()
        messagebox.showinfo("Added", "Student added successfully")

    def edit_student(self):
        messagebox.showinfo("Edit", "Edit function coming soon")

    def delete_student(self):
        selected = self.student_table.focus()
        if not selected:
            messagebox.showwarning("Select", "Select a student first")
            return
        self.student_table.delete(selected)
        self.update_student_count()

    def search_student(self):
        keyword = self.search_student_var.get().lower()
        for item in self.student_table.get_children():
            if keyword in str(self.student_table.item(item, "values")).lower():
                self.student_table.selection_set(item)
                self.student_table.see(item)
                return
        messagebox.showinfo("Search", "Student not found")


if __name__ == "__main__":
    root = tk.Tk()
    app = Student(root)
    root.mainloop()
