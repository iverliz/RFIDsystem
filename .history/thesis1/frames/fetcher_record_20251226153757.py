import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import ImageTk, Image
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from utils.database import db_connect

# Directory to save photos
PHOTO_DIR = os.path.join(BASE_DIR, "fetcher_photos")
os.makedirs(PHOTO_DIR, exist_ok=True)

class Fetcher(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg="#b2e5ed")
        self.root = root
        self.photo_path = None

        root.title("RFID MANAGEMENT SYSTEM - FETCHER RECORD")
        root.geometry("1350x700+0+0")
        self.pack(fill="both", expand=True)

        # Header
        header = tk.Frame(self, height=95, bg="#0047AB")
        header.pack(fill="x")
        tk.Label(header, text="FETCHER INFORMATION", font=("Arial", 24, "bold"),
                 bg="#0047AB", fg="white").place(x=50, y=25)

        # Left box
        self.left_box = tk.Frame(self, width=500, height=550, bg="white")
        self.left_box.place(x=50, y=125)
        self.left_box.pack_propagate(False)

        # Photo frame
        self.photo_frame = tk.Frame(self.left_box, width=200, height=200,
                                    bg="#E0E0E0", bd=2, relief="ridge")
        self.photo_frame.place(x=20, y=20)
        self.photo_frame.pack_propagate(False)

        self.photo_label = tk.Label(self.photo_frame, bg="#E0E0E0")
        self.photo_label.pack(fill="both", expand=True)

        tk.Button(self.left_box, text="Upload Photo", width=15,
                  command=self.upload_photo).place(x=60, y=240)

        # Fetcher details
        y = 290
        self.fetcher_name_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.contact_var = tk.StringVar()

        fields = [("Fetcher Name:", self.fetcher_name_var),
                  ("Address:", self.address_var),
                  ("Contact Number:", self.contact_var)]

        for i, (label, var) in enumerate(fields):
            tk.Label(self.left_box, text=label, bg="white", font=("Arial", 12)).place(x=20, y=y + i*40)
            tk.Entry(self.left_box, textvariable=var, font=("Arial", 12), width=30).place(x=160, y=y + i*40)

        # Action buttons
        tk.Button(self.left_box, text="ADD", width=10, font=("Arial", 12, "bold"),
                  bg="#4CAF50", fg="white", command=self.add_fetcher).place(x=40, y=510)

        tk.Button(self.left_box, text="EDIT", width=10, font=("Arial", 12, "bold"),
                  bg="#2196F3", fg="white", command=self.edit_fetcher).place(x=180, y=510)

        tk.Button(self.left_box, text="DELETE", width=10, font=("Arial", 12, "bold"),
                  bg="#F44336", fg="white", command=self.delete_fetcher).place(x=320, y=510)

        # Right panel
        self.right_panel = tk.Frame(self, width=550, height=500, bg="white", bd=2, relief="groove")
        self.right_panel.place(x=700, y=150)
        self.right_panel.pack_propagate(False)

        tk.Label(self.right_panel, text="Search Fetcher", font=("Arial", 16, "bold"), bg="white").place(x=20, y=20)
        self.search_var = tk.StringVar()
        tk.Entry(self.right_panel, textvariable=self.search_var, font=("Arial", 12), width=25).place(x=20, y=60)
        tk.Button(self.right_panel, text="Search", width=10, command=self.search_fetcher).place(x=300, y=57)

        self.fetcher_count_var = tk.StringVar(value="Total Fetchers: 0")
        tk.Label(self.right_panel, textvariable=self.fetcher_count_var,
                 font=("Arial", 12, "bold"), bg="white", fg="#0047AB").place(x=20, y=100)

        # Table
        columns = ("fetcher_name", "address", "contact")
        self.fetcher_table = ttk.Treeview(self.right_panel, columns=columns, show="headings", height=12)
        for col in columns:
            self.fetcher_table.heading(col, text=col.replace("_", " ").title())
            self.fetcher_table.column(col, width=150)
        self.fetcher_table.place(x=20, y=140, width=500)

        self.load_data()

    # Upload photo
    def upload_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if path:
            img = Image.open(path).resize((200,200))
            self.photo = ImageTk.PhotoImage(img)
            self.photo_label.config(image=self.photo)
            self.photo_label.image = self.photo
            self.photo_path = path

    # Check if contact number exists
    def contact_exists(self, contact):
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT contact FROM fetcher WHERE contact=%s", (contact,))
            return cursor.fetchone() is not None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # Load data into table
    def load_data(self):
        self.fetcher_table.delete(*self.fetcher_table.get_children())
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT fetcher_name, address, contact FROM fetcher")
            rows = cursor.fetchall()
            for row in rows:
                self.fetcher_table.insert("", "end", values=row)
            self.fetcher_count_var.set(f"Total Fetchers: {len(rows)}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # Add fetcher
    def add_fetcher(self):
        name = self.fetcher_name_var.get()
        address = self.address_var.get()
        contact = self.contact_var.get()

        if not all([name, address, contact, self.photo_path]):
            messagebox.showerror("Error", "All fields and photo are required")
            return

        if self.contact_exists(contact):
            messagebox.showerror("Error", "This contact number already exists")
            return

        img_save_path = os.path.join(PHOTO_DIR, f"fetcher_{contact}.jpg")
        Image.open(self.photo_path).save(img_save_path)

        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO fetcher (fetcher_name, address, contact, photo_path)
                VALUES (%s,%s,%s,%s)
            """, (name, address, contact, img_save_path))
            conn.commit()
            messagebox.showinfo("Success", "Fetcher added successfully")
            self.clear_fields()
            self.load_data()
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # Edit fetcher
    def edit_fetcher(self):
        contact = self.contact_var.get()
        if not contact:
            messagebox.showerror("Error", "Contact number is required to edit")
            return

        name = self.fetcher_name_var.get()
        address = self.address_var.get()
        img_save_path = None
        if self.photo_path:
            img_save_path = os.path.join(PHOTO_DIR, f"fetcher_{contact}.jpg")
            Image.open(self.photo_path).save(img_save_path)

        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            if img_save_path:
                cursor.execute("""
                    UPDATE fetcher SET fetcher_name=%s, address=%s, photo_path=%s
                    WHERE contact=%s
                """, (name, address, img_save_path, contact))
            else:
                cursor.execute("""
                    UPDATE fetcher SET fetcher_name=%s, address=%s
                    WHERE contact=%s
                """, (name, address, contact))
            conn.commit()
            messagebox.showinfo("Success", "Fetcher updated successfully")
            self.clear_fields()
            self.load_data()
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # Delete fetcher
    def delete_fetcher(self):
        contact = self.contact_var.get()
        if not contact:
            messagebox.showerror("Error", "Contact number is required to delete")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete fetcher with contact {contact}?")
        if not confirm:
            return

        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM fetcher WHERE contact=%s", (contact,))
            if cursor.rowcount == 0:
                messagebox.showerror("Error", "Fetcher not found")
            else:
                conn.commit()
                messagebox.showinfo("Success", "Fetcher deleted successfully")
                self.clear_fields()
                self.load_data()
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # Search fetcher
    def search_fetcher(self):
        keyword = self.search_var.get()
        self.fetcher_table.delete(*self.fetcher_table.get_children())
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT fetcher_name, address, contact
                FROM fetcher
                WHERE fetcher_name LIKE %s OR address LIKE %s
            """, (f"%{keyword}%", f"%{keyword}%"))
            rows = cursor.fetchall()
            for row in rows:
                self.fetcher_table.insert("", "end", values=row)
            self.fetcher_count_var.set(f"Total Fetchers: {len(rows)}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # Clear input fields
    def clear_fields(self):
        self.fetcher_name_var.set("")
        self.address_var.set("")
        self.contact_var.set("")
        self.photo_label.config(image="")
        self.photo_path = None

if __name__ == "__main__":
    root = tk.Tk()
    app = Fetcher(root)
    root.mainloop()
