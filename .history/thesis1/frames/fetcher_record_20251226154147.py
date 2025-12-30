import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import ImageTk, Image
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from utils.database import db_connect

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

        # ===== HEADER =====
        header = tk.Frame(self, height=95, bg="#0047AB", bd=2, relief="groove")
        header.pack(fill="x")
        tk.Label(header, text="FETCHER INFORMATION",
                 font=("Arial", 24, "bold"), bg="#0047AB", fg="white").place(x=50, y=25)

        # ===== LEFT PANEL =====
        self.left_panel = tk.Frame(self, width=500, height=550, bg="white", bd=2, relief="groove")
        self.left_panel.place(x=50, y=125)
        self.left_panel.pack_propagate(False)

        # ===== PHOTO =====
        self.photo_frame = tk.Frame(self.left_panel, width=200, height=200, bg="#E0E0E0", bd=2, relief="ridge")
        self.photo_frame.place(x=20, y=20)
        self.photo_label = tk.Label(self.photo_frame, bg="#E0E0E0")
        self.photo_label.pack(fill="both", expand=True)
        tk.Button(self.left_panel, text="Upload Photo", command=self.upload_photo).place(x=60, y=240)

        # ===== VARIABLES =====
        self.fetcher_name_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.contact_var = tk.StringVar()

        fields = [
            ("Fetcher Name", self.fetcher_name_var),
            ("Address", self.address_var),
            ("Contact Number", self.contact_var)
        ]

        y = 290
        for i, (label, var) in enumerate(fields):
            tk.Label(self.left_panel, text=label, bg="white", font=("Arial", 12)).place(x=20, y=y + i*40)
            tk.Entry(self.left_panel, textvariable=var, font=("Arial", 12), width=30).place(x=160, y=y + i*40)

        # ===== BUTTONS =====
        tk.Button(self.left_panel, text="ADD", bg="#4CAF50", fg="white", command=self.add_fetcher).place(x=40, y=450)
        tk.Button(self.left_panel, text="EDIT", bg="#2196F3", fg="white", command=self.edit_fetcher).place(x=180, y=450)
        tk.Button(self.left_panel, text="DELETE", bg="#F44336", fg="white", command=self.delete_fetcher).place(x=320, y=450)

        # ===== RIGHT PANEL =====
        self.right_panel = tk.Frame(self, width=550, height=500, bg="white", bd=2, relief="groove")
        self.right_panel.place(x=700, y=150)

        tk.Label(self.right_panel, text="Search Fetcher", font=("Arial", 16, "bold"), bg="white").place(x=20, y=20)
        self.search_var = tk.StringVar()
        tk.Entry(self.right_panel, textvariable=self.search_var, width=25).place(x=20, y=60)
        tk.Button(self.right_panel, text="Search", command=self.search_fetcher).place(x=300, y=57)

        columns = ("contact", "fetcher_name", "address")
        self.fetcher_table = ttk.Treeview(self.right_panel, columns=columns, show="headings", height=12)
        self.fetcher_table.heading("contact", text="Contact")
        self.fetcher_table.heading("fetcher_name", text="Fetcher Name")
        self.fetcher_table.heading("address", text="Address")
        self.fetcher_table.column("contact", width=120)
        self.fetcher_table.column("fetcher_name", width=180)
        self.fetcher_table.column("address", width=180)
        self.fetcher_table.place(x=20, y=140, width=500)

        self.load_data()

    # ===== FUNCTIONS =====
    def upload_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if path:
            img = Image.open(path).resize((200, 200))
            self.photo = ImageTk.PhotoImage(img)
            self.photo_label.config(image=self.photo)
            self.photo_label.image = self.photo
            self.photo_path = path

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

    def load_data(self):
        self.fetcher_table.delete(*self.fetcher_table.get_children())
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT contact, fetcher_name, address FROM fetcher")
            for row in cursor.fetchall():
                self.fetcher_table.insert("", "end", values=row)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def add_fetcher(self):
        name = self.fetcher_name_var.get()
        address = self.address_var.get()
        contact = self.contact_var.get()

        if not all([name, address, contact, self.photo_path]):
            messagebox.showerror("Error", "All fields and photo are required")
            return

        if self.contact_exists(contact):
            messagebox.showerror("Error", "Contact number already exists")
            return

        # Save photo
        img_save = os.path.join(PHOTO_DIR, f"fetcher_{contact}.jpg")
        Image.open(self.photo_path).save(img_save)

        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO fetcher (fetcher_name, address, contact, photo_path)
                VALUES (%s,%s,%s,%s)
            """, (name, address, contact, img_save))
            conn.commit()
            self.load_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Fetcher added successfully")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def edit_fetcher(self):
        contact = self.contact_var.get()
        if not self.contact_exists(contact):
            messagebox.showerror("Error", "Fetcher not found")
            return

        name = self.fetcher_name_var.get()
        address = self.address_var.get()

        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE fetcher SET fetcher_name=%s, address=%s
                WHERE contact=%s
            """, (name, address, contact))
            conn.commit()
            self.load_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Fetcher updated successfully")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def delete_fetcher(self):
        contact = self.contact_var.get()
        if not self.contact_exists(contact):
            messagebox.showerror("Error", "Fetcher not found")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Delete fetcher {contact}?")
        if not confirm:
            return

        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM fetcher WHERE contact=%s", (contact,))
            conn.commit()
            self.load_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Fetcher deleted successfully")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def clear_fields(self):
        self.fetcher_name_var.set("")
        self.address_var.set("")
        self.contact_var.set("")
        self.photo_label.config(image="")
        self.photo_path = None

    def search_fetcher(self):
        keyword = self.search_var.get()
        self.fetcher_table.delete(*self.fetcher_table.get_children())
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT contact, fetcher_name, address FROM fetcher WHERE fetcher_name LIKE %s", (f"%{keyword}%",))
            for row in cursor.fetchall():
                self.fetcher_table.insert("", "end", values=row)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = Fetcher(root)
    root.mainloop()
