import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import ImageTk, Image
import os
import sys

# ================= PATH SETUP =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.database import db_connect

PHOTO_DIR = os.path.join(BASE_DIR, "fetcher_photos")
os.makedirs(PHOTO_DIR, exist_ok=True)


class FetcherRecord(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#b2e5ed")
        self.controller = controller
        self.photo_path = None

        # ================= HEADER =================
        header = tk.Frame(self, height=70, bg="#0047AB")
        header.pack(fill="x")

        tk.Label(
            header,
            text="FETCHER INFORMATION",
            font=("Arial", 20, "bold"),
            bg="#0047AB",
            fg="white"
        ).place(x=30, y=18)

        # ================= LEFT PANEL =================
        self.left_box = tk.Frame(self, width=430, height=460, bg="white", bd=2, relief="groove")
        self.left_box.place(x=40, y=90)
        self.left_box.pack_propagate(False)

        # ================= PHOTO =================
        self.photo_frame = tk.Frame(self.left_box, width=160, height=160, bg="#E0E0E0", bd=2, relief="ridge")
        self.photo_frame.place(x=20, y=20)
        self.photo_frame.pack_propagate(False)

        self.photo_label = tk.Label(self.photo_frame, bg="#E0E0E0")
        self.photo_label.pack(fill="both", expand=True)

        tk.Button(
            self.left_box,
            text="Upload Photo",
            width=14,
            command=self.upload_photo
        ).place(x=210, y=80)

        # ================= VARIABLES =================
        self.fetcher_id = None
        self.fetcher_name_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.contact_var = tk.StringVar()

        # ================= FORM =================
        fields = [
            ("Fetcher Name:", self.fetcher_name_var),
            ("Address:", self.address_var),
            ("Contact Number:", self.contact_var),
        ]

        y = 200
        for i, (label, var) in enumerate(fields):
            tk.Label(self.left_box, text=label, bg="white", font=("Arial", 11)).place(x=20, y=y + i * 35)
            tk.Entry(self.left_box, textvariable=var, width=30, font=("Arial", 11)).place(x=150, y=y + i * 35)

        # ================= BUTTONS =================
        btn_frame = tk.Frame(self.left_box, bg="white")
        btn_frame.place(x=40, y=320)

        tk.Button(
            btn_frame,
            text="ADD",
            width=10,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.add_fetcher
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            btn_frame,
            text="EDIT",
            width=10,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.edit_fetcher
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            btn_frame,
            text="DELETE",
            width=10,
            bg="#F44336",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.delete_fetcher
        ).grid(row=0, column=2, padx=5)

        # ================= RIGHT PANEL =================
        self.right_panel = tk.Frame(self, width=500, height=460, bg="white", bd=2, relief="groove")
        self.right_panel.place(x=520, y=90)
        self.right_panel.pack_propagate(False)

        tk.Label(
            self.right_panel,
            text="Search Fetcher",
            font=("Arial", 14, "bold"),
            bg="white"
        ).place(x=20, y=15)

        self.search_var = tk.StringVar()
        tk.Entry(self.right_panel, textvariable=self.search_var, width=25, font=("Arial", 11)).place(x=20, y=50)
        tk.Button(self.right_panel, text="Search", width=10, command=self.search_fetcher).place(x=260, y=47)

        self.fetcher_count_var = tk.StringVar(value="Total Fetchers: 0")
        tk.Label(
            self.right_panel,
            textvariable=self.fetcher_count_var,
            font=("Arial", 11, "bold"),
            fg="#0047AB",
            bg="white"
        ).place(x=20, y=85)

        # ================= TABLE =================
        self.fetcher_table = ttk.Treeview(
            self.right_panel,
            columns=("id", "Fetcher_name", "Address", "Contact", "photo"),
            show="headings",
            height=12
        )

        self.fetcher_table.heading("Fetcher_name", text="Fetcher Name")
        self.fetcher_table.heading("Address", text="Address")
        self.fetcher_table.heading("Contact", text="Contact")
        self.fetcher_table.heading("id", text="ID")  # hidden
        self.fetcher_table.heading("photo", text="Photo")  # hidden

        self.fetcher_table.column("id", width=0, stretch=False)
        self.fetcher_table.column("photo", width=0, stretch=False)
        self.fetcher_table.column("Fetcher_name", width=180)
        self.fetcher_table.column("Address", width=180)
        self.fetcher_table.column("Contact", width=120)

        self.fetcher_table.place(x=20, y=120, width=450)
        self.fetcher_table.bind("<<TreeviewSelect>>", self.on_table_select)

        self.load_data()

    # ================= FUNCTIONS =================
    def upload_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if path:
            img = Image.open(path).resize((160, 160))
            self.photo = ImageTk.PhotoImage(img)
            self.photo_label.config(image=self.photo)
            self.photo_label.image = self.photo
            self.photo_path = path

    def load_data(self):
        self.fetcher_table.delete(*self.fetcher_table.get_children())
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT ID, Fetcher_name, Address, contact, photo_path FROM fetcher")
            rows = cursor.fetchall()
            for row in rows:
                self.fetcher_table.insert("", "end", values=row)
            self.fetcher_count_var.set(f"Total Fetchers: {len(rows)}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def add_fetcher(self):
        if not all([self.fetcher_name_var.get(), self.address_var.get(), self.contact_var.get(), self.photo_path]):
            messagebox.showerror("Error", "All fields and photo are required")
            return

        filename = f"{self.fetcher_name_var.get().replace(' ', '_')}.jpg"
        img_save = os.path.join(PHOTO_DIR, filename)
        Image.open(self.photo_path).convert("RGB").save(img_save, "JPEG")

        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO fetcher (Fetcher_name, Address, contact, photo_path) VALUES (%s,%s,%s,%s)",
                (self.fetcher_name_var.get(), self.address_var.get(), self.contact_var.get(), img_save)
            )
            conn.commit()
            self.load_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Fetcher added successfully")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def edit_fetcher(self):
        selected = self.fetcher_table.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a fetcher first")
            return

        fetcher_id, _, _, _, old_photo = self.fetcher_table.item(selected, "values")

        # If new photo uploaded
        if self.photo_path and self.photo_path != old_photo:
            filename = f"{self.fetcher_name_var.get().replace(' ', '_')}.jpg"
            img_save = os.path.join(PHOTO_DIR, filename)
            Image.open(self.photo_path).convert("RGB").save(img_save, "JPEG")
        else:
            img_save = old_photo

        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE fetcher SET Fetcher_name=%s, Address=%s, contact=%s, photo_path=%s WHERE fetcher_id=%s",
                (self.fetcher_name_var.get(), self.address_var.get(), self.contact_var.get(), img_save, fetcher_id)
            )
            conn.commit()
            self.load_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Fetcher updated successfully")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def delete_fetcher(self):
        selected = self.fetcher_table.focus()
        if not selected:
            return

        ID, _, _, _, photo_path = self.fetcher_table.item(selected, "values")
        if not messagebox.askyesno("Confirm", "Delete this fetcher?"):
            return

        # Delete from DB and remove photo file
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM fetcher WHERE ID=%s", (ID,))
            conn.commit()
            if photo_path and os.path.exists(photo_path):
                os.remove(photo_path)
            self.load_data()
            self.clear_fields()
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def search_fetcher(self):
        keyword = self.search_var.get()
        self.fetcher_table.delete(*self.fetcher_table.get_children())
        conn = cursor = None
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT ID, Fetcher_name, Address, contact, photo_path FROM fetcher WHERE Fetcher_name LIKE %s",
                (f"%{keyword}%",)
            )
            rows = cursor.fetchall()
            for row in rows:
                self.fetcher_table.insert("", "end", values=row)
            self.fetcher_count_var.set(f"Total Fetchers: {len(rows)}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def clear_fields(self):
        self.fetcher_id = None
        self.fetcher_name_var.set("")
        self.address_var.set("")
        self.contact_var.set("")
        self.photo_label.config(image="")
        self.photo_label.image = None
        self.photo_path = None

    def on_table_select(self, event):
        selected = self.fetcher_table.focus()
        if not selected:
            return

        self.fetcher_id, name, address, contact, photo_path = self.fetcher_table.item(selected, "values")
        self.fetcher_name_var.set(name)
        self.address_var.set(address)
        self.contact_var.set(contact)

        if photo_path and os.path.exists(photo_path):
            img = Image.open(photo_path).resize((160, 160))
            self.photo = ImageTk.PhotoImage(img)
            self.photo_label.config(image=self.photo)
            self.photo_label.image = self.photo
            self.photo_path = photo_path
