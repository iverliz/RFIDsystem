import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import ImageTk, Image
import os
import sys
import time

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
        
        # ================= STATE VARIABLES =================
        self.photo_path = None
        self.photo = None # Reference to prevent garbage collection
        self.edit_mode = False
        self.current_fetcher_id = None

        # ================= PAGINATION & SEARCH STATE =================
        self.page_size = 50
        self.current_page = 1
        self.total_fetchers = 0
        self.search_results = []
        self.search_page = 1

        # ================= HEADER =================
        header = tk.Frame(self, height=70, bg="#0047AB")
        header.pack(fill="x")
        tk.Label(header, text="FETCHER INFORMATION",
                 font=("Arial", 20, "bold"), bg="#0047AB", fg="white").place(x=30, y=18)

        # ================= LEFT PANEL (FORM) =================
        self.left_box = tk.Frame(self, width=430, height=480, bg="white", bd=2, relief="groove")
        self.left_box.place(x=40, y=90)
        self.left_box.pack_propagate(False)

        # Photo UI
        self.photo_frame = tk.Frame(self.left_box, width=160, height=160, bg="#E0E0E0", bd=2, relief="ridge")
        self.photo_frame.place(x=20, y=20)
        self.photo_frame.pack_propagate(False)

        self.photo_label = tk.Label(self.photo_frame, bg="#E0E0E0")
        self.photo_label.pack(fill="both", expand=True)

        self.upload_btn = tk.Button(self.left_box, text="Upload Photo", width=14, command=self.upload_photo)
        self.upload_btn.place(x=210, y=70)

        # NEW: Remove Photo Button (Applied from Student Record)
        self.remove_btn = tk.Button(self.left_box, text="Remove Photo", width=14, fg="red", command=self.remove_photo_action)
        self.remove_btn.place(x=210, y=105)

        self.edit_label = tk.Label(self.left_box, text="VIEW MODE", font=("Arial", 10, "bold"), fg="gray", bg="white")
        self.edit_label.place(x=280, y=10)

        # Form Variables
        self.fetcher_name_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.contact_var = tk.StringVar()

        fields = [
            ("Fetcher Name:", self.fetcher_name_var),
            ("Address:", self.address_var),
            ("Contact Number:", self.contact_var),
        ]
        
        self.entries = []
        y = 200
        for i, (label, var) in enumerate(fields):
            tk.Label(self.left_box, text=label, bg="white", font=("Arial", 11)).place(x=20, y=y + i * 35)
            ent = tk.Entry(self.left_box, textvariable=var, width=30, font=("Arial", 11))
            ent.place(x=150, y=y + i * 35)
            self.entries.append(ent)

        # Action Buttons
        btn_frame = tk.Frame(self.left_box, bg="white")
        btn_frame.place(x=15, y=330)
        
        self.add_btn = tk.Button(btn_frame, text="ADD", width=9, bg="#4CAF50", fg="white", 
                                 font=("Arial", 9, "bold"), command=self.add_fetcher)
        self.add_btn.grid(row=0, column=0, padx=2)

        self.edit_btn = tk.Button(btn_frame, text="EDIT", width=9, bg="#2196F3", fg="white", 
                                  font=("Arial", 9, "bold"), command=self.enable_edit_mode)
        self.edit_btn.grid(row=0, column=1, padx=2)

        self.update_btn = tk.Button(btn_frame, text="UPDATE", width=9, bg="#FF9800", fg="white", 
                                    font=("Arial", 9, "bold"), command=self.update_fetcher_db, state="disabled")
        self.update_btn.grid(row=0, column=2, padx=2)

        self.delete_btn = tk.Button(btn_frame, text="DELETE", width=9, bg="#F44336", fg="white", 
                                    font=("Arial", 9, "bold"), command=self.delete_fetcher)
        self.delete_btn.grid(row=0, column=3, padx=2)

        # ================= RIGHT PANEL (TABLE & SEARCH) =================
        self.right_panel = tk.Frame(self, width=500, height=480, bg="white", bd=2, relief="groove")
        self.right_panel.place(x=520, y=90)
        self.right_panel.pack_propagate(False)

        tk.Label(self.right_panel, text="Search Fetcher", font=("Arial", 14, "bold"), bg="white").place(x=20, y=15)
        self.search_var = tk.StringVar()
        tk.Entry(self.right_panel, textvariable=self.search_var, width=25, font=("Arial", 11)).place(x=20, y=50)
        tk.Button(self.right_panel, text="Search", command=self.search_fetcher).place(x=260, y=47)
        tk.Button(self.right_panel, text="Clear", command=self.clear_search).place(x=320, y=47)

        self.fetcher_count_var = tk.StringVar(value="Total: 0 | Page 1/1")
        tk.Label(self.right_panel, textvariable=self.fetcher_count_var, font=("Arial", 11, "bold"),
                 fg="#0047AB", bg="white").place(x=20, y=85)

        # Table
        columns = ("id", "Fetcher_name", "Address", "Contact")
        self.fetcher_table = ttk.Treeview(self.right_panel, columns=columns, show="headings", height=12)
        self.fetcher_table.heading("id", text="ID")
        self.fetcher_table.heading("Fetcher_name", text="Fetcher Name")
        self.fetcher_table.heading("Address", text="Address")
        self.fetcher_table.heading("Contact", text="Contact")
        self.fetcher_table.column("id", width=40)
        self.fetcher_table.column("Fetcher_name", width=160)
        self.fetcher_table.column("Address", width=140)
        self.fetcher_table.column("Contact", width=100)
        self.fetcher_table.place(x=20, y=120, width=450)
        self.fetcher_table.bind("<<TreeviewSelect>>", self.on_table_select)

        # Pagination
        nav = tk.Frame(self.right_panel, bg="white")
        nav.place(x=160, y=420)
        tk.Button(nav, text="◀ Prev", command=self.prev_page).grid(row=0, column=0, padx=5)
        tk.Button(nav, text="Next ▶", command=self.next_page).grid(row=0, column=1, padx=5)

        self.reset_ui_state()
        self.load_data()

    # ================= HELPERS & UI CONTROL =================
    def display_photo(self, path):
        """Displays photo or shows placeholder (Applied from Student Record)."""
        try:
            if path and os.path.exists(path):
                img = Image.open(path).resize((160, 160))
                self.photo = ImageTk.PhotoImage(img)
                self.photo_label.config(image=self.photo, text="")
                self.photo_label.image = self.photo
            else:
                # Default text placeholder
                self.photo_label.config(image="", text="NO PHOTO\nAVAILABLE", 
                                        font=("Arial", 10, "bold"), fg="#666666")
                self.photo = None
        except Exception:
            self.photo_label.config(image="", text="Error Loading Image")

    def upload_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if path:
            self.photo_path = path
            self.display_photo(path)

    def remove_photo_action(self):
        """Logic to default the record (Applied from Student Record)."""
        if self.add_btn["text"] == "SAVE" or self.edit_mode:
            if messagebox.askyesno("Confirm", "Remove photo from this record?"):
                self.photo_path = None
                self.display_photo(None)
        else:
            messagebox.showwarning("Warning", "Enable Edit Mode or Add Mode to change photos.")

    def set_fields_state(self, state):
        for ent in self.entries: ent.config(state=state)
        self.upload_btn.config(state=state)
        self.remove_btn.config(state=state)

    def reset_ui_state(self):
        self.edit_mode = False
        self.current_fetcher_id = None
        self.set_fields_state("disabled")
        self.add_btn.config(text="ADD", state="normal", bg="#4CAF50")
        self.edit_btn.config(state="normal", bg="#2196F3")
        self.delete_btn.config(text="DELETE", bg="#F44336")
        self.update_btn.config(state="disabled")
        self.edit_label.config(text="VIEW MODE", fg="gray", bg="white")
        self.clear_fields()

    def clear_fields(self):
        self.fetcher_name_var.set("")
        self.address_var.set("")
        self.contact_var.set("")
        self.display_photo(None)
        self.photo_path = None
        self.fetcher_table.selection_remove(self.fetcher_table.selection())

    # ================= DATA LOGIC =================
    def load_data(self):
        self.fetcher_table.delete(*self.fetcher_table.get_children())
        offset = (self.current_page - 1) * self.page_size
        try:
            with db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM fetcher")
                    self.total_fetchers = cursor.fetchone()[0]
                    cursor.execute("SELECT ID, Fetcher_name, Address, contact FROM fetcher ORDER BY Fetcher_name LIMIT %s OFFSET %s", 
                                   (self.page_size, offset))
                    for row in cursor.fetchall():
                        self.fetcher_table.insert("", "end", values=row)

            total_p = max(1, (self.total_fetchers + self.page_size - 1) // self.page_size)
            self.fetcher_count_var.set(f"Total: {self.total_fetchers} | Page {self.current_page}/{total_p}")
        except Exception as e:
            print(f"Load error: {e}")

    def search_fetcher(self):
        keyword = self.search_var.get().strip()
        if not keyword: return self.clear_search()
        try:
            with db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT ID, Fetcher_name, Address, contact FROM fetcher WHERE Fetcher_name LIKE %s OR Address LIKE %s",
                                   (f"%{keyword}%", f"%{keyword}%"))
                    self.search_results = cursor.fetchall()
            self.search_page = 1
            self.update_search_table()
        except Exception as e:
            messagebox.showerror("Search Error", str(e))

    def update_search_table(self):
        self.fetcher_table.delete(*self.fetcher_table.get_children())
        start = (self.search_page - 1) * self.page_size
        end = start + self.page_size
        page_data = self.search_results[start:end]
        for row in page_data: 
            self.fetcher_table.insert("", "end", values=row)
        
        total_p = max(1, (len(self.search_results) + self.page_size - 1) // self.page_size)
        self.fetcher_count_var.set(f"Found: {len(self.search_results)} | Page {self.search_page}/{total_p}")

    def clear_search(self):
        self.search_var.set("")
        self.search_results = []
        self.current_page = 1
        self.load_data()

    def next_page(self):
        if self.search_var.get().strip():
            if self.search_page * self.page_size < len(self.search_results):
                self.search_page += 1
                self.update_search_table()
        elif self.current_page * self.page_size < self.total_fetchers:
            self.current_page += 1
            self.load_data()

    def prev_page(self):
        if self.search_var.get().strip():
            if self.search_page > 1:
                self.search_page -= 1
                self.update_search_table()
        elif self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    # ================= CRUD OPERATIONS =================
    def add_fetcher(self):
        if self.add_btn["text"] == "ADD":
            self.reset_ui_state()
            self.set_fields_state("normal")
            self.add_btn.config(text="SAVE", bg="#2E7D32")
            self.edit_btn.config(state="disabled")
            self.delete_btn.config(text="CANCEL", bg="#757575")
            return

        if not all([self.fetcher_name_var.get().strip(), self.address_var.get().strip()]):
            return messagebox.showerror("Error", "Name and Address are required")

        try:
            photo_save = None
            if self.photo_path:
                filename = f"f_{int(time.time())}.jpg"
                photo_save = os.path.join(PHOTO_DIR, filename)
                Image.open(self.photo_path).convert("RGB").save(photo_save, "JPEG")

            with db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("INSERT INTO fetcher (Fetcher_name, Address, contact, photo_path) VALUES (%s,%s,%s,%s)",
                                   (self.fetcher_name_var.get().strip(), self.address_var.get().strip(), self.contact_var.get().strip(), photo_save))
                    conn.commit()
            
            messagebox.showinfo("Success", "Fetcher added successfully")
            self.reset_ui_state()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add: {e}")

    def enable_edit_mode(self):
        if not self.current_fetcher_id:
            return messagebox.showwarning("Warning", "Select a fetcher first")
        self.edit_mode = True
        self.set_fields_state("normal")
        self.add_btn.config(state="disabled")
        self.delete_btn.config(text="CANCEL", bg="#757575")
        self.update_btn.config(state="normal")
        self.edit_label.config(text="EDIT MODE", fg="white", bg="red")

    def update_fetcher_db(self):
        if not self.current_fetcher_id: return
        
        sql_parts = ["Fetcher_name=%s", "Address=%s", "contact=%s"]
        params = [self.fetcher_name_var.get().strip(), self.address_var.get().strip(), self.contact_var.get().strip()]

        # LOGIC: If photo_path is None, update database to NULL (Remove the photo)
        if self.photo_path is None:
            sql_parts.append("photo_path=NULL")
        elif not self.photo_path.startswith(PHOTO_DIR):
            filename = f"f_{int(time.time())}.jpg"
            photo_save = os.path.join(PHOTO_DIR, filename)
            Image.open(self.photo_path).convert("RGB").save(photo_save, "JPEG")
            sql_parts.append("photo_path=%s")
            params.append(photo_save)

        params.append(self.current_fetcher_id)
        query = f"UPDATE fetcher SET {', '.join(sql_parts)} WHERE ID=%s"

        try:
            with db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    conn.commit()
            messagebox.showinfo("Success", "Updated successfully")
            self.reset_ui_state()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_fetcher(self):
        if self.delete_btn["text"] == "CANCEL":
            self.reset_ui_state()
            return
        if not self.current_fetcher_id: return
        if not messagebox.askyesno("Confirm", "Permanently delete this fetcher and their photo?"): return

        try:
            with db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT photo_path FROM fetcher WHERE ID=%s", (self.current_fetcher_id,))
                    path = cursor.fetchone()[0]
                    if path and os.path.exists(path): os.remove(path)
                    cursor.execute("DELETE FROM fetcher WHERE ID=%s", (self.current_fetcher_id,))
                    conn.commit()
            self.reset_ui_state()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_table_select(self, _):
        if self.edit_mode or self.add_btn["text"] == "SAVE": return
        
        sel = self.fetcher_table.focus()
        if not sel: return

        data = self.fetcher_table.item(sel, "values")
        self.current_fetcher_id = data[0]
        self.fetcher_name_var.set(data[1])
        self.address_var.set(data[2])
        self.contact_var.set(data[3])

        try:
            with db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT photo_path FROM fetcher WHERE ID=%s", (self.current_fetcher_id,))
                    row = cursor.fetchone()
                    path = row[0] if row else None
                    self.photo_path = path
                    self.display_photo(path)
        except:
            self.display_photo(None)