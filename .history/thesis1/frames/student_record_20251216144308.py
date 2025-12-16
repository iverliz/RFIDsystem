import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import ImageTk, Image
import os


class Student(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg="#b2e5ed")
        self.root = root

        root.title("RFID MANAGEMENT SYSTEM - STUDENT RECORD")
        root.geometry("1350x700+0+0")

        self.pack(fill="both", expand=True)

        # ================= HEADER =================
        self.student_frame = tk.Frame(
            self,
            height=95,
            bg="#0047AB",
            bd=2,
            relief="groove"
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
            self,
            width=500,
            height=500,
            bg="white",
            bd=2,
            relief="groove"
        )
        self.student_left.place(x=50, y=150)
        self.student_left.pack_propagate(False)

        # ================= PHOTO FRAME =================
        self.photo_frame = tk.Frame(
            self.student_left,
            width=200,
            height=200,
            bg="#E0E0E0",
            bd=2,
            relief="ridge"
        )
        self.photo_frame.place(x=20, y=20)
        self.photo_frame.pack_propagate(False)

        self.photo_label = tk.Label(self.photo_frame, bg="#E0E0E0")
        self.photo_label.pack(fill="both", expand=True)

        # ================= BUTTON BELOW PHOTO =================
        tk.Button(
            self.student_left,
            text="Upload Photo",
            width=15,
            command=self.upload_photo
        ).place(x=60, y=240)

        # ================= STUDENT DETAILS =================
        y_start = 290
        label_font = ("Arial", 12)
        entry_font = ("Arial", 12)

        # Full Name
        tk.Label(
            self.student_left,
            text="Full Name:",
            bg="white",
            font=label_font
        ).place(x=20, y=y_start)

        self.fullname_var = tk.StringVar()
        tk.Entry(
            self.student_left,
            textvariable=self.fullname_var,
            font=entry_font,
            width=30
        ).place(x=160, y=y_start)

        # Grade Level
        tk.Label(
            self.student_left,
            text="Grade Level:",
            bg="white",
            font=label_font
        ).place(x=20, y=y_start + 40)

        self.grade_var = tk.StringVar()
        tk.Entry(
            self.student_left,
            textvariable=self.grade_var,
            font=entry_font,
            width=30
        ).place(x=160, y=y_start + 40)

        # Student ID
        tk.Label(
            self.student_left,
            text="Student ID:",
            bg="white",
            font=label_font
        ).place(x=20, y=y_start + 80)

        self.student_id_var = tk.StringVar()
        tk.Entry(
            self.student_left,
            textvariable=self.student_id_var,
            font=entry_font,
            width=30
        ).place(x=160, y=y_start + 80)

        # Guardian Name
        tk.Label(
            self.student_left,
            text="Guardian Name:",
            bg="white",
            font=label_font
        ).place(x=20, y=y_start + 120)

        self.guardian_name_var = tk.StringVar()
        tk.Entry(
            self.student_left,
            textvariable=self.guardian_name_var,
            font=entry_font,
            width=30
        ).place(x=160, y=y_start + 120)

        # Guardian Contact
        tk.Label(
            self.student_left,
            text="Guardian Contact:",
            bg="white",
            font=label_font
        ).place(x=20, y=y_start + 160)

        self.guardian_contact_var = tk.StringVar()
        tk.Entry(
            self.student_left,
            textvariable=self.guardian_contact_var,
            font=entry_font,
            width=30
        ).place(x=160, y=y_start + 160)

        # ================= ACTION BUTTONS =================
        btn_y = y_start + 210

        tk.Button(
    self.student_left,
    text="ADD",
    width=10,
    font=("Arial", 12, "bold"),
    bg="#4CAF50",
    fg="white",
    command=self.add_student
).place(x=40, y=btn_y)

        tk.Button(
    self.student_left,
    text="EDIT",
    width=10,
    font=("Arial", 12, "bold"),
    bg="#2196F3",
    fg="white",
    command=self.edit_student
).place(x=180, y=btn_y)

        tk.Button(
    self.student_left,
    text="DELETE",
    width=10,
    font=("Arial", 12, "bold"),
    bg="#F44336",
    fg="white",
    command=self.delete_student
).place(x=320, y=btn_y)


    # ================= UPLOAD FUNCTION =================
    def upload_photo(self):
        file_path = filedialog.askopenfilename(
            title="Select Student Photo",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )

        if not file_path:
            return

        img = Image.open(file_path)
        img = img.resize((200, 200))
        self.photo = ImageTk.PhotoImage(img)

        self.photo_label.config(image=self.photo)
        self.photo_label.image = self.photo  # prevent garbage collection

    def add_student(self):
        messagebox.showinfo(
        "Add Student",
        f"Student Added:\n\n"
        f"Name: {self.fullname_var.get()}\n"
        f"Grade: {self.grade_var.get()}\n"
        f"Student ID: {self.student_id_var.get()}"
    )

    def edit_student(self):
        messagebox.showinfo(
        "Edit Student",
        "Student record updated successfully."
    )

    def delete_student(self):
        confirm = messagebox.askyesno(
        "Delete Student",
        "Are you sure you want to delete this student?"
    )
        if confirm:
            self.clear_student_fields()
        messagebox.showinfo("Deleted", "Student record deleted.")

    def clear_student_fields(self):
    for var in (
        self.fullname_var,
        self.grade_var,
        self.student_id_var,
        self.guardian_name_var,
        self.guardian_contact_var
    ):
        var.set("")
    self.photo_label.config(image="")


if __name__ == "__main__":
    root = tk.Tk()
    app = Student(root)
    root.mainloop()
