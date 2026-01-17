import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import ImageTk, Image
import os
import time
import sys
# Make sure your database utility is correctly accessible
from utils.database import db_connect

# ================= PATH SETUP =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTO_DIR = os.path.join(BASE_DIR, "teacher_photos")
os.makedirs(PHOTO_DIR, exist_ok=True)
sys.path.append(BASE_DIR)

class TeacherRecord(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#b2e5ed")
        self.controller = controller

        self.photo_path = None  
        self.photo = None
        self.edit_mode = False
        self.current_teacher_id = None

        # ================= PAGINATION =================
        self.page_size = 50
        self.current_page = 1
        self.total_teachers = 0
        self.search_results = None
        self.search_page = 1

        # ================= HEADER =================
        header = tk.Frame(self, height=70, bg="#0047AB")
        header.pack(fill="x")
        tk.Label(header, text="TEACHER INFORMATION",
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
        self.teacher_name_var = tk.StringVar()
        self.teacher_grade_var = tk.StringVar()

        # ================= FORM =================
        tk.Label(self.left_box, text="Teacher Name:", bg="white", font=("Arial", 11)).place(x=20, y=200)
        self.name_entry = tk.Entry(self.left_box, textvariable=self.teacher_name_var, width=30, font=("Arial", 11))
        self.name_entry.place(x=150, y=200)

        tk.Label(self.left_box, text="Grade:", bg="white", font=("Arial", 11)).place(x=20, y=240)
        self.grade_entry = tk.Entry(self.left_box, textvariable=self.teacher_grade_var, width=30, font=("Arial", 11))
        self.grade_entry.place(x=150, y=240)

        # ================= BUTTONS =================
        btn_frame = tk.Frame(self.left_box, bg="white")
        btn_frame.place(x=15, y=320)

        self.add_btn = tk.Button(btn_frame, text="ADD", width=9, bg="#4CAF50", fg="white", 
                                 font=("Arial", 9, "bold"), command=self.add_teacher)
        self.add_btn.grid(row=0, column=0, padx=2)

        self.edit_btn = tk.Button(btn_frame, text="EDIT", width=9, bg="#2196F3", fg="white", 
                                  font=("Arial", 9, "bold"), command=self.enable_edit_mode)
        self.edit_btn.grid(row=0, column=1, padx=2)

        self.update_btn = tk.Button(btn_frame, text="UPDATE", width=9, bg="#FF9800", fg="white", 
                                    font=("Arial", 9, "bold"), command=self.update_teacher_db)
        self.update_btn.grid(row=0, column=2, padx=2)

        self.delete_btn = tk.Button(btn_frame, text="DELETE", width=9, bg="#F44336", fg="white", 
                                    font=("Arial", 9, "bold"), command=self.delete_teacher)
        self.delete_btn.grid(row=0, column=3, padx=2)

        # ================= RIGHT PANEL =================
        self.right_panel = tk.Frame(self, width=500, height=480, bg="white", bd=2, relief="groove")
        self.right_panel.place(x=520, y=90)
        self.right_panel.pack_propagate(False)

        tk.Label(self.right_panel, text="Search Teacher", font=("Arial", 14, "bold"), bg="white").place(x=20, y=15)

        self.search_var = tk.StringVar()
        tk.Entry(self.right_panel, textvariable=self.search_var, width=25, font=("Arial", 11)).place(x=20, y=50)
        tk.Button(self.right_panel, text="Search", command=self.search_teacher).place(x=260, y=47)
        tk.Button(self.right_panel, text="Clear", command=self.clear_search).place(x=320, y=47)

        self.teacher_count_var = tk.StringVar(value="Total Teachers: 0 | Page 1/1")
        tk.Label(self.right_panel, textvariable=self.teacher_count_var, font=("Arial", 11, "bold"), fg="#0047AB", bg="white").place(x=20, y=85)

        # ================= TABLE =================
        columns = ("teacher_id", "name", "grade")
        self.teacher_table = ttk.Treeview(self.right_panel, columns=columns, show="headings", height=12)
        self.teacher_table.heading("teacher_id", text="ID")
        self.teacher_table.heading("name", text="Teacher Name")
        self.teacher_table.heading("grade", text="Grade")
        self.teacher_table.column("teacher_id", width=50)
        self.teacher_table.column("name", width=240)
        self.teacher_table.column("grade", width=120)
        self.teacher_table.place(x=20, y=120, width=450)
        self.teacher_table.bind("<<TreeviewSelect>>", self.on_select)

        # ================= PAGINATION BUTTONS =================
        nav = tk.Frame(self.right_panel, bg="white")
        nav.place(x=160, y=420)
        tk.Button(nav, text="◀ Prev", command=self.prev_page).grid(row=0, column=0, padx=5)
        tk.Button(nav, text="Next ▶", command=self.next_page).grid(row=0, column=1, padx=5)

        # ================= INITIALIZE =================
        self.reset_ui_state()
        self.load_teachers()

    # ================= STATE CONTROL =================
    def set_fields_state(self, state):
        self.name_entry.config(state=state)
        self.grade_entry.config(state=state)
        self.upload_btn.config(state=state)

    def reset_ui_state(self):
        self.edit_mode = False
        self.current_teacher_id = None
        self.set_fields_state("disabled")
        
        self.add_btn.config(text="ADD", state="normal", bg="#4CAF50")
        self.edit_btn.config(state="normal")
        self.delete_btn.config(text="DELETE", bg="#F44336")
        self.update_btn.config(state="disabled")
        self.edit_label.config(text="VIEW MODE", fg="gray", bg="white")
        self.clear_fields()

    # ================= HELPERS =================
    def load_image(self, path, size=(160, 160)):
        try:
            img = Image.open(path).resize(size)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def upload_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if path:
            self.photo_path = path
            self.photo = self.load_image(path)
            if self.photo:
                self.photo_label.config(image=self.photo)
                self.photo_label.image = self.photo

    def validate_fields(self):
        if not self.teacher_name_var.get().strip(): return "Teacher Name is required"
        if not self.teacher_grade_var.get().isdigit(): return "Grade must be numeric"
        return None

    # ================= CRUD OPERATIONS =================
    def add_teacher(self):
        if self.add_btn["text"] == "ADD":
            self.reset_ui_state()
            self.set_fields_state("normal")
            self.add_btn.config(text="SAVE", bg="#2E7D32")
            self.edit_btn.config(state="disabled")
            self.delete_btn.config(text="CANCEL", bg="#757575")
            return

        error = self.validate_fields()
        if error: return messagebox.showerror("Error", error)

        try:
            photo_save = None
            if self.photo_path:
                filename = f"t_{int(time.time())}.jpg"
                photo_save = os.path.join(PHOTO_DIR, filename)
                Image.open(self.photo_path).convert("RGB").save(photo_save, "JPEG")

            with db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("INSERT INTO teacher (teacher_name, teacher_grade, photo_path) VALUES (%s, %s, %s)",
                                   (self.teacher_name_var.get().strip(), int(self.teacher_grade_var.get()), photo_save))
                    conn.commit()
            
            messagebox.showinfo("Success", "Teacher added")
            self.reset_ui_state()
            self.load_teachers()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error saving teacher: {e}")

    def enable_edit_mode(self):
        if not self.teacher_name_var.get():
            return messagebox.showwarning("Warning", "Select a teacher from the table first")
        
        self.edit_mode = True
        self.set_fields_state("normal")
        self.add_btn.config(state="disabled")
        self.delete_btn.config(text="CANCEL", bg="#757575")
        self.update_btn.config(state="normal")
        self.edit_label.config(text="EDIT MODE", fg="white", bg="red")

    def update_teacher_db(self):
        error = self.validate_fields()
        if error: return messagebox.showerror("Error", error)

        try:
            with db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT photo_path FROM teacher WHERE teacher_id=%s", (self.current_teacher_id,))
                    old_photo = cursor.fetchone()[0]
                    photo_save = old_photo

                    if self.photo_path and not self.photo_path.startswith(PHOTO_DIR):
                        if old_photo and os.path.exists(old_photo):
                            try: os.remove(old_photo)
                            except: pass
                        filename = f"t_{int(time.time())}.jpg"
                        photo_save = os.path.join(PHOTO_DIR, filename)
                        Image.open(self.photo_path).convert("RGB").save(photo_save, "JPEG")

                    cursor.execute("UPDATE teacher SET teacher_name=%s, teacher_grade=%s, photo_path=%s WHERE teacher_id=%s",
                                   (self.teacher_name_var.get().strip(), int(self.teacher_grade_var.get()), photo_save, self.current_teacher_id))
                    conn.commit()
            
            messagebox.showinfo("Success", "Teacher updated")
            self.reset_ui_state()
            self.load_teachers()
        except Exception as e:
            messagebox.showerror("Error", f"Update failed: {e}")

    def delete_teacher(self):
        if self.delete_btn["text"] == "CANCEL":
            self.reset_ui_state()
            return

        if not self.current_teacher_id: return messagebox.showwarning("Warning", "Select a teacher")
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this teacher?"): return

        try:
            with db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT photo_path FROM teacher WHERE teacher_id=%s", (self.current_teacher_id,))
                    p = cursor.fetchone()[0]
                    if p and os.path.exists(p): os.remove(p)
                    cursor.execute("DELETE FROM teacher WHERE teacher_id=%s", (self.current_teacher_id,))
                    conn.commit()
            self.reset_ui_state()
            self.load_teachers()
        except Exception as e:
            messagebox.showerror("Error", f"Delete failed: {e}")

    # ================= DATA LOADING & PAGINATION =================
    def load_teachers(self, is_search=False):
        self.teacher_table.delete(*self.teacher_table.get_children())
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
                        cursor.execute("SELECT COUNT(*) FROM teacher")
                        self.total_teachers = cursor.fetchone()[0]
                        cursor.execute("SELECT teacher_id, teacher_name, teacher_grade FROM teacher ORDER BY teacher_name LIMIT %s OFFSET %s", (self.page_size, offset))
                        page_data = cursor.fetchall()
                        total = self.total_teachers

            for row in page_data: self.teacher_table.insert("", "end", values=row)
            
            curr = self.search_page if is_search else self.current_page
            total_p = max(1, (total + self.page_size - 1) // self.page_size)
            self.teacher_count_var.set(f"Total: {total} | Page {curr}/{total_p}")
        except Exception as e:
            print(f"Load error: {e}")

    def search_teacher(self):
        word = self.search_var.get().strip()
        if not word: return self.clear_search()
        
        try:
            with db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT teacher_id, teacher_name, teacher_grade FROM teacher WHERE teacher_name LIKE %s", (f"%{word}%",))
                    self.search_results = cursor.fetchall()
            self.search_page = 1
            self.load_teachers(is_search=True)
        except: pass

    def clear_search(self):
        self.search_var.set("")
        self.search_results = None
        self.current_page = 1
        self.load_teachers()

    def next_page(self):
        if self.search_results:
            if self.search_page * self.page_size < len(self.search_results):
                self.search_page += 1
                self.load_teachers(is_search=True)
        elif self.current_page * self.page_size < self.total_teachers:
            self.current_page += 1
            self.load_teachers()

    def prev_page(self):
        if self.search_results:
            if self.search_page > 1:
                self.search_page -= 1
                self.load_teachers(is_search=True)
        elif self.current_page > 1:
            self.current_page -= 1
            self.load_teachers()

    def on_select(self, _):
        if self.edit_mode or self.add_btn["text"] == "SAVE": return
        
        sel = self.teacher_table.focus()
        if not sel: return
        
        data = self.teacher_table.item(sel, "values")
        self.current_teacher_id = data[0]
        self.teacher_name_var.set(data[1])
        self.teacher_grade_var.set(data[2])

        try:
            with db_connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT photo_path FROM teacher WHERE teacher_id=%s", (self.current_teacher_id,))
                    path = cursor.fetchone()[0]
                    if path and os.path.exists(path):
                        self.photo = self.load_image(path)
                        self.photo_label.config(image=self.photo)
                        self.photo_path = path
                    else:
                        self.photo_label.config(image="")
                        self.photo_path = None
        except: pass

    def clear_fields(self):
        self.teacher_name_var.set("")
        self.teacher_grade_var.set("")
        self.photo_label.config(image="")
        self.photo_path = None