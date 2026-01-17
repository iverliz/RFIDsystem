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
        self.photo_path = None
        self.photo = None
        self.edit_mode = False
        self.current_fetcher_id = None

        # ================= PAGINATION & SEARCH STATE =================
        self.page_size = 50
        self.current_page = 1
        self.total_fetchers = 0
        self.search_results = None
        self.search_page = 1

        # ================= HEADER =================
        header = tk.Frame(self, height=70, bg="#0047AB")
        header.pack(fill="x")
        tk.Label(header, text="FETCHER INFORMATION",
                 font=("Arial", 20, "bold"), bg="#0047AB", fg="white").place(x=30, y=18)

        # ================= LEFT PANEL =================
        self.left_box = tk.Frame(self, width=430, height=480, bg="white", bd=2, relief="groove")
        self.left_box.place(x=40, y=90)
        self.left_box.pack_propagate(False)

        # ================= PHOTO =================
        self.photo_frame = tk.Frame(self.left_box, width=160, height=160, bg="#E0E0E0", bd=2, relief="ridge")
        self.photo_frame.place(x=20, y=20)
        self.photo_frame.pack_propagate(False)

        self.photo_label = tk.Label(self.photo_frame, bg="#E0E0E0")
        self.photo_label.pack(fill="both", expand=True)

        self.upload_btn = tk.Button(self.left_box, text="Upload Photo", width=14, command=self.upload_photo)
        self.upload_btn.place(x=210, y=80)

        self.edit_label = tk.Label(self.left_box, text="VIEW MODE", font=("Arial", 10, "bold"), fg="gray", bg="white")
        self.edit_label.place(x=280, y=10)

        # ================= VARIABLES =================
        self.fetcher_name_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.contact_var = tk.StringVar()

        # ================= FORM =================
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

        # ================= BUTTONS =================
        btn_frame = tk.Frame(self.left_box, bg="white")
        btn_frame.place(x=15, y=330)
        
        self.add_btn = tk.Button(btn_frame, text="ADD", width=9, bg="#4CAF50", fg="white", 
                                 font=("Arial", 9, "bold"), command=self.add_fetcher)
        self.add_btn.grid(row=0, column=0, padx=2)

        self.edit_btn = tk.Button(btn_frame, text="EDIT", width=9, bg="#2196F3", fg="white", 
                                  font=("Arial", 9, "bold"), command=self.enable_edit_mode)
        self.edit_btn.grid(row=0, column=1, padx=2)

        self.update_btn = tk.Button(btn_frame, text="UPDATE", width=9, bg="#FF9800", fg="white", 
                                    font=("Arial", 9, "bold"), command=self.update_fetcher_db)
        self.update_btn.grid(row=0, column=2, padx=2)

        self.delete_btn = tk.Button(btn_frame, text="DELETE", width=9, bg="#F44336", fg="white", 
                                    font=("Arial", 9, "bold"), command=self.delete_fetcher)
        self.delete_btn.grid(row=0, column=3, padx=2)

        # ================= RIGHT PANEL =================
        self.right_panel = tk.Frame(self, width=500, height=480, bg="white", bd=2, relief="groove")
        self.right_panel.place(x=520, y=90)
        self.right_panel.pack_propagate(False)

        tk.Label(self.right_panel, text="Search Fetcher", font=("Arial", 14, "bold"), bg="white").place(x=20, y=15)
        self.search_var = tk.StringVar()
        tk.Entry(self.right_panel, textvariable=self.search_var, width=25, font=("Arial", 11)).place(x=20, y=50)
        tk.Button(self.right_panel, text="Search", command=self.search_fetcher).place(x=260, y=47)
        tk.Button(self.right_panel, text="Clear", command=self.clear_search).place(x=320, y=47)

        self.fetcher_count_var = tk.StringVar(value="Total Fetchers: 0 | Page 1/1")
        tk.Label(self.right_panel, textvariable=self.fetcher_count_var, font=("Arial", 11, "bold"),
                 fg="#0047AB", bg="white").place(x=20, y=85)

        # ================= TABLE =================
        self.fetcher_table = ttk.Treeview(self.right_panel,
                                          columns=("id", "Fetcher_name", "Address", "Contact"),
                                          show="headings", height=12)

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

        # ================= PAGINATION BUTTONS =================
        nav = tk.Frame(self.right_panel, bg="white")
        nav.place(x=160, y=420)
        tk.Button(nav, text="◀ Prev", command=self.prev_page).grid(row=0, column=0, padx=5)
        tk.Button(nav, text="Next ▶", command=self.next_page).grid(row=0, column=1, padx=5)

        # ================= INITIALIZE =================
        self.reset_ui_state()
        self.load_data()

    # ================= UI STATE MANAGEMENT =================
    def set_fields_state(self, state):
        for ent in self.entries: ent.config(state=state)
        self.upload_btn.config(state=state)

    def reset_ui_state(self):
        self.edit_mode = False
        self.current_fetcher_id = None
        self.set_fields_state("disabled")
        self.add_btn.config(text="ADD", state="normal", bg="#4CAF50")
        self.edit_btn.config(state="normal")
        self.delete_btn.config(text="DELETE", bg="#F44336")
        self.update_btn.config(state="disabled")
        self.edit_label.config(text="VIEW MODE", fg="gray", bg="white")
        self.clear_fields()

    # ================= PHOTO HELPERS =================
    def upload_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if path:
            try:
                img = Image.open(path).resize((160, 160))
                self.photo = ImageTk.PhotoImage(img)
                self.photo_label.config(image=self.photo)
                self.photo_label.image = self.photo
                self.photo_path = path
            except Exception as e:
                messagebox.showerror("Error", f"Could not load image: {e}")

    # ================= DATA LOADING & SEARCH =================
    def load_data(self, is_search=False):
        self.fetcher_table.delete(*self.fetcher_table.get_children())
        try:
            if is_search and self.search_results is not None:
                data_source = self.search_results
                total = len(data_source)
                start = (self.search_page - 1) * self.page_size
                page_data = data_source[start : start + self.page_size]
            else:
                offset = (self.current_page - 1) * self.page_size
                with db_connect() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT COUNT(*) FROM fetcher")
                        self.total_fetchers = cursor.fetchone()[0]
                        cursor.execute("SELECT ID, Fetcher_name, Address, contact FROM fetcher ORDER BY Fetcher_name LIMIT %s OFFSET %s", 
                                       (self.page_size, offset))
                        page_data = cursor.fetchall()
                        total = self.total_fetchers

            for row in page_data: self.fetcher_table.insert("", "end", values=row)
            
            curr = self.search_page if is_search else self.current_page
            total_p = max(1, (total + self.page_size - 1) // self.page_size)
            self.fetcher_count_var.set(f"Total: {total} | Page {curr}/{total_p}")
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
            self.load_data(is_search=True)
        except Exception as e:
            messagebox.showerror("Search Error", str(e))

    def clear_search(self):
        self.search_var.set("")
        self.search_results = None
        self.current_page = 1
        self.load_data()

    def next_page(self):
        if self.search_results:
            if self.search_page * self.page_size < len(self.search_results):
                self.search_page += 1
                self.load_data(is_search=True)
        elif self.current_page * self.page_size < self.total_fetchers:
            self.current_page += 1
            self.load_data()

    def prev_page(self):
        if self.search_results:
            if self.search_page > 1:
                self.search_page -= 1
                self.load_data(is_search=True)
        elif self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    # ================= CRUD =================
    def add_fetcher(self):
        if self.add_btn["text"] == "ADD":
            self.reset_ui_state()
            self.set_fields_state("normal")
            self.add_btn.config(text="SAVE", bg="#2E7D32")
            self.edit_btn.config(state="disabled")
            self.delete_btn.config(text="CANCEL", bg="#757575")
            return

        if not all([self.fetcher_name_var.get(), self.address_var.get(), self.contact_var.get(), self.photo_path]):
            messagebox.showerror("Error", "All fields and photo are required")
            return

        try:
            filename = f"f_{int(time.time())}.jpg"
            img_save = os.path.join(PHOTO_DIR, filename)
            Image.open(self.photo_path).convert("RGB").save(img_save, "JPEG")

            with db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("INSERT INTO fetcher (Fetcher_name, Address, contact, photo_path) VALUES (%s,%s,%s,%s)",
                                   (self.fetcher_name_var.get(), self.address_var.get(), self.contact_var.get(), img_save))
                    conn.commit()
            
            messagebox.showinfo("Success", "Fetcher added")
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
        try:
            with db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT photo_path FROM fetcher WHERE ID=%s", (self.current_fetcher_id,))
                    old_photo = cursor.fetchone()[0]
                    img_save = old_photo

                    if self.photo_path and not self.photo_path.startswith(PHOTO_DIR):
                        filename = f"f_{int(time.time())}.jpg"
                        img_save = os.path.join(PHOTO_DIR, filename)
                        Image.open(self.photo_path).convert("RGB").save(img_save, "JPEG")

                    cursor.execute("UPDATE fetcher SET Fetcher_name=%s, Address=%s, contact=%s, photo_path=%s WHERE ID=%s",
                                   (self.fetcher_name_var.get(), self.address_var.get(), self.contact_var.get(), img_save, self.current_fetcher_id))
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
        if not messagebox.askyesno("Confirm", "Delete this fetcher?"): return

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

    # ================= TABLE SELECTION =================
    def on_table_select(self, event):
        if self.edit_mode or self.add_btn["text"] == "SAVE": return
        
        selected = self.fetcher_table.focus()
        if not selected: return

        data = self.fetcher_table.item(selected, "values")
        self.current_fetcher_id = data[0]
        self.fetcher_name_var.set(data[1])
        self.address_var.set(data[2])
        self.contact_var.set(data[3])

        try:
            with db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT photo_path FROM fetcher WHERE ID=%s", (self.current_fetcher_id,))
                    p_path = cursor.fetchone()[0]
                    if p_path and os.path.exists(p_path):
                        img = Image.open(p_path).resize((160, 160))
                        self.photo = ImageTk.PhotoImage(img)
                        self.photo_label.config(image=self.photo)
                        self.photo_path = p_path
                    else:
                        self.photo_label.config(image="")
        except: pass

    def clear_fields(self):
        self.fetcher_name_var.set("")
        self.address_var.set("")
        self.contact_var.set("")
        self.photo_label.config(image="")
        self.photo_path = None