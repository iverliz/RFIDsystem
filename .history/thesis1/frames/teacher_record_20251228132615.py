import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import ImageTk, Image


class TeacherInfo(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg="#b2e5ed")
        self.root = root

        root.title("TEACHER MANAGEMENT SYSTEM - TEACHER RECORD")
        root.geometry("1350x700+0+0")

        self.pack(fill="both", expand=True)

        # ================= HEADER =================
        self.header = tk.Frame(self, height=95, bg="#0047AB", bd=2, relief="groove")
        self.header.pack(fill="x")

        tk.Label(
            self.header,
            text="TEACHER INFORMATION",
            font=("Arial", 24, "bold"),
            bg="#0047AB",
            fg="white"
        ).place(x=50, y=25)

        # ================= LEFT BOX =================
        self.left_box = tk.Frame(self, width=500, height=550, bg="white", bd=2, relief="groove")
        self.left_box.place(x=50, y=125)
        self.left_box.pack_propagate(False)

        # ================= PHOTO FRAME =================
        self.photo_frame = tk.Frame(
            self.left_box, width=200, height=200,
            bg="#E0E0E0", bd=2, relief="ridge"
        )
        self.photo_frame.place(x=20, y=20)
        self.photo_frame.pack_propagate(False)

        self.photo_label = tk.Label(self.photo_frame, bg="#E0E0E0")
        self.photo_label.pack(fill="both", expand=True)

        tk.Button(
            self.left_box,
            text="Upload Photo",
            width=15,
            command=self.upload_photo
        ).place(x=60, y=240)

        # ================= TEACHER DETAILS =================
        y = 290
        label_font = ("Arial", 12)
        entry_font = ("Arial", 12)

        self.teacher_name_var = tk.StringVar()
        self.teacher_grade_var = tk.StringVar()

        fields = [
            ("Teacher Name:", self.teacher_name_var),
            ("Grade:", self.teacher_grade_var),
        ]

        for i, (label, var) in enumerate(fields):
            tk.Label(self.left_box, text=label, bg="white",
                     font=label_font).place(x=20, y=y + i * 40)
            tk.Entry(self.left_box, textvariable=var,
                     font=entry_font, width=30).place(x=160, y=y + i * 40)

        # ================= ACTION BUTTONS =================
        tk.Button(
            self.left_box, text="ADD", width=10,
            font=("Arial", 12, "bold"),
            bg="#4CAF50", fg="white",
            command=self.add_teacher
        ).place(x=40, y=510)

        tk.Button(
            self.left_box, text="EDIT", width=10,
            font=("Arial", 12, "bold"),
            bg="#2196F3", fg="white",
            command=self.edit_teacher
        ).place(x=180, y=510)

        tk.Button(
            self.left_box, text="DELETE", width=10,
            font=("Arial", 12, "bold"),
            bg="#F44336", fg="white",
            command=self.delete_teacher
        ).place(x=320, y=510)

        # ================= RIGHT PANEL =================
        self.right_panel = tk.Frame(self, width=550, height=500, bg="white", bd=2, relief="groove")
        self.right_panel.place(x=700, y=150)
        self.right_panel.pack_propagate(False)

        tk.Label(
            self.right_panel,
            text="Search Teacher",
            font=("Arial", 16, "bol1d"),
            bg="white"
        ).place(x=20, y=20)

        self.search_var = tk.StringVar()
        tk.Entry(
            self.right_panel,
            textvariable=self.search_var,
            font=("Arial", 12),
            width=25
        ).place(x=20, y=60)

        tk.Button(
            self.right_panel,
            text="Search",
            width=10,
            command=self.search_teacher
        ).place(x=300, y=57)

        self.teacher_count_var = tk.StringVar(value="Total Teachers: 0")
        tk.Label(
            self.right_panel,
            textvariable=self.teacher_count_var,
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#0047AB"
        ).place(x=20, y=100)

        columns = ("name", "grade")
        self.teacher_table = ttk.Treeview(
            self.right_panel,
            columns=columns,
            show="headings",
            height=12
        )

        headings = ["Teacher Name", "Grade", ""]
        for col, text in zip(columns, headings):
            self.teacher_table.heading(col, text=text)
            self.teacher_table.column(col, width=160)

        self.teacher_table.place(x=20, y=140, width=500)

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

    def update_teacher_count(self):
        count = len(self.teacher_table.get_children())
        self.teacher_count_var.set(f"Total Teachers: {count}")

    def add_teacher(self):
        self.teacher_table.insert("", "end", values=(
            self.teacher_name_var.get(),
            self.subject_var.get(),
            self.contact_var.get()
        ))
        self.update_teacher_count()
        messagebox.showinfo("Added", "Teacher added successfully")

    def edit_teacher(self):
        messagebox.showinfo("Edit", "Edit function coming soon")

    def delete_teacher(self):
        selected = self.teacher_table.focus()
        if not selected:
            messagebox.showwarning("Select", "Select a teacher first")
            return
        self.teacher_table.delete(selected)
        self.update_teacher_count()

    def search_teacher(self):
        keyword = self.search_var.get().lower()
        for item in self.teacher_table.get_children():
            if keyword in str(self.teacher_table.item(item, "values")).lower():
                self.teacher_table.selection_set(item)
                self.teacher_table.see(item)
                return
        messagebox.showinfo("Search", "Teacher not found")


if __name__ == "__main__":
    root = tk.Tk()
    app = TeacherInfo(root)
    root.mainloop()
