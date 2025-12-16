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

        


if __name__ == "__main__":
    root = tk.Tk()
    app = Student(root)
    root.mainloop()
