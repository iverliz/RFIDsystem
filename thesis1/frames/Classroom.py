import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import io
import os
import sys

# Ensure utility imports work
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from utils.database import db_connect

class ClassroomFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#F0F4F8")
        self.controller = controller
        
        # 1. Get Session Data
        self.user_data = getattr(
            self.controller,
            "current_user",
            {"role": "Teacher", "username": "Guest"}
        )
        self.username = self.user_data.get("username")
        
        # 2. Sync Teacher Name from DB
        self.real_teacher_name = self.get_teacher_display_name()
        self.last_log_id = None  
        self.current_photo = None # Keep reference to avoid garbage collection
        
        # Start background loop
        self.check_for_updates() 

        # ================= HEADER =================
        header = tk.Frame(self, bg="#0047AB", height=80)
        header.pack(fill="x")

        tk.Label(
            header,
            text="🍎 TEACHER DASHBOARD",
            font=("Helvetica", 20, "bold"),
            bg="#0047AB",
            fg="white"
        ).pack(side="left", padx=20, pady=15)
        
        tk.Button(
            header,
            text="🔄 REFRESH",
            command=self.refresh_tables,
            bg="#2196F3",
            fg="white",
            bd=0,
            padx=10
        ).pack(side="right", padx=10, pady=25)

        tk.Label(
            header,
            text=f"Active: {self.real_teacher_name}",
            font=("Helvetica", 10),
            bg="#0047AB",
            fg="#B0C4DE"
        ).pack(side="right", padx=10)

        # ================= MAIN LAYOUT =================
        main_body = tk.Frame(self, bg="#F0F4F8")
        main_body.pack(fill="both", expand=True, padx=20, pady=10)

        left_col = tk.Frame(main_body, bg="#F0F4F8")
        left_col.pack(side="left", fill="both", expand=True)

        self.right_col = tk.Frame(
            main_body,
            bg="white",
            width=300,
            highlightthickness=1,
            highlightbackground="#D1D9E6"
        )
        self.right_col.pack(side="right", fill="y", padx=(15, 0))
        
        self.setup_profile_panel()
        self.setup_tables(left_col)

        # Bind event
        self.student_table.bind("<<TreeviewSelect>>", self.on_student_select)
        self.refresh_tables()

    # ================= DATABASE =================

    def get_teacher_display_name(self):
        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT Teacher_name FROM teacher WHERE Teacher_name = %s",
                        (self.username,)
                    )
                    res = cur.fetchone()
                    return res[0] if res else self.username
        except Exception as e:
            print("Teacher Lookup Error:", e)
            return self.username

    # ================= TABLE & UI SETUP =================

    def setup_tables(self, parent):
        action_panel = tk.Frame(
            parent,
            bg="white",
            highlightthickness=1,
            highlightbackground="#D1D9E6"
        )
        action_panel.pack(fill="x", pady=(0, 15), ipady=10)

        # Row 0: Student ID Input
        tk.Label(action_panel, text="STUDENT ID:", font=("Arial", 10, "bold"), bg="white").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        
        self.search_id_var = tk.StringVar()
        self.search_id_var.trace_add("write", self.verify_student_id)
        self.id_entry = tk.Entry(action_panel, textvariable=self.search_id_var, width=15, font=("Arial", 11))
        self.id_entry.grid(row=0, column=1, padx=5, sticky="w")

        # Row 1: Name Verification
        tk.Label(action_panel, text="CONFIRM NAME:", font=("Arial", 10, "bold"), bg="white").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        
        self.found_name_var = tk.StringVar(value="Enter ID...")
        self.name_display = tk.Label(action_panel, textvariable=self.found_name_var, font=("Arial", 11, "italic"), bg="white", fg="#0047AB")
        self.name_display.grid(row=1, column=1, sticky="w")

        # Column 2: Control Buttons
        btn_frame = tk.Frame(action_panel, bg="white")
        btn_frame.grid(row=0, column=2, rowspan=2, padx=20)

        self.add_btn = tk.Button(
            btn_frame, text="ADD TO CLASS", bg="#4CAF50", fg="white", 
            font=("Arial", 9, "bold"), width=16, state="disabled", command=self.add_student_to_class
        )
        self.add_btn.pack(pady=2)

        self.remove_btn = tk.Button(
            btn_frame, text="REMOVE FROM CLASS", bg="#F44336", fg="white", 
            font=("Arial", 9, "bold"), width=16, state="disabled", command=self.remove_student_from_class
        )
        self.remove_btn.pack(pady=2)

        tk.Label(parent, text="My Enrolled Students", font=("Arial", 12, "bold"), bg="#F0F4F8", fg="#0047AB").pack(anchor="w")

        self.columns = ("ID", "Student ID", "Full Name", "Fetcher Code")
        self.student_table = self.create_table(parent, self.columns)

    def create_table(self, parent, cols):
        frame = tk.Frame(parent)
        frame.pack(fill="both", expand=True, pady=(5, 15))
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=12)
        for c in cols:
            tree.heading(c, text=c.upper())
            tree.column(c, width=100, anchor="center")
        tree.column("Full Name", width=200, anchor="w")
        tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        return tree

    def setup_profile_panel(self):
        tk.Label(self.right_col, text="STUDENT PROFILE", font=("Arial", 11, "bold"), bg="white", fg="#0047AB").pack(pady=15)

        self.photo_label = tk.Label(self.right_col, text="No Image", bg="#E1E8EE", width=25, height=10, relief="solid", bd=1)
        self.photo_label.pack(pady=10, padx=20)

        self.info_label = tk.Label(self.right_col, text="Select a student...", bg="white", justify="left", font=("Arial", 10), wraplength=250)
        self.info_label.pack(pady=20, padx=15, fill="x")
        
        tk.Label(self.right_col, text="📌 RECENT FETCH LOGS", font=("Arial", 10, "bold"), bg="white", fg="#0047AB").pack(pady=(10, 5))

        history_frame = tk.Frame(self.right_col, bg="white")
        history_frame.pack(fill="both", expand=True, padx=5, pady=5)

        cols = ("Time", "Fetcher", "Loc")
        self.history_table = ttk.Treeview(history_frame, columns=cols, show="headings", height=8)
        self.history_table.heading("Time", text="TIME")
        self.history_table.heading("Fetcher", text="BY")
        self.history_table.heading("Loc", text="LOC")
        self.history_table.column("Time", width=100, anchor="center")
        self.history_table.column("Fetcher", width=80, anchor="w")
        self.history_table.column("Loc", width=40, anchor="center")
        self.history_table.pack(side="left", fill="both", expand=True)
        
        h_scroll = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_table.yview)
        self.history_table.configure(yscrollcommand=h_scroll.set)
        h_scroll.pack(side="right", fill="y")

    # ================= LOGIC =================

    def verify_student_id(self, *args):
        sid = self.search_id_var.get().strip()
        if not sid:
            self.found_name_var.set("Enter ID...")
            self.add_btn.config(state="disabled")
            return

        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT Student_name FROM student WHERE Student_id = %s", (sid,))
                    res = cur.fetchone()
                    if res:
                        self.found_name_var.set(res[0])
                        self.name_display.config(fg="green")
                        self.add_btn.config(state="normal")
                    else:
                        self.found_name_var.set("ID Not Found")
                        self.name_display.config(fg="red")
                        self.add_btn.config(state="disabled")
        except Exception as e:
            print("Verify Error:", e)

    def add_student_to_class(self):
        sid = self.search_id_var.get().strip()
        sname = self.found_name_var.get()
        if not messagebox.askyesno("Confirm", f"Add {sname} to your class?"): return

        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT teacher_name FROM classroom WHERE student_id = %s", (sid,))
                    if cur.fetchone():
                        messagebox.showerror("Error", "Student already assigned to a teacher.")
                        return
                    cur.execute("INSERT INTO classroom (teacher_name, student_id) VALUES (%s, %s)", (self.real_teacher_name, sid))
                    conn.commit()
            self.search_id_var.set("")
            self.refresh_tables()
            messagebox.showinfo("Success", f"{sname} added.")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def remove_student_from_class(self):
        sel = self.student_table.focus()
        if not sel: return
        data = self.student_table.item(sel, "values")
        sid, sname = data[1], data[2]

        if not messagebox.askyesno("Remove", f"Remove {sname} from your class?"): return

        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM classroom WHERE student_id = %s AND teacher_name = %s", (sid, self.real_teacher_name))
                    conn.commit()
            self.refresh_tables()
            self.info_label.config(text="Select a student...")
            self.photo_label.config(image='', text="No Image")
            messagebox.showinfo("Success", "Student removed.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_tables(self):
        self.student_table.delete(*self.student_table.get_children())
        self.remove_btn.config(state="disabled")
        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT s.ID, s.Student_id, s.Student_name, s.fetcher_code
                        FROM student s
                        INNER JOIN classroom c ON s.Student_id = c.student_id
                        WHERE c.teacher_name = %s
                    """, (self.real_teacher_name,))
                    for row in cur.fetchall():
                        self.student_table.insert("", "end", values=row)
        except Exception as e:
            print("Refresh Error:", e)

    def on_student_select(self, event):
        sel = self.student_table.focus()
        if not sel: return
        data = self.student_table.item(sel, "values")
        self.remove_btn.config(state="normal")
        self.load_full_student_details(data[1])

    def load_full_student_details(self, student_id):
        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT Student_name, Student_id, Guardian_name, Guardian_contact, photo_path FROM student WHERE Student_id = %s", (student_id,))
                    res = cur.fetchone()
                    if res:
                        name, sid, guard, contact, photo_blob = res
                        self.info_label.config(text=f"NAME: {name}\nID: {sid}\nGUARDIAN: {guard}\nCONTACT: {contact}")
                        
                        # Fix Image Display
                        if photo_blob:
                            try:
                                stream = io.BytesIO(photo_blob)
                                img = Image.open(stream)
                                img = img.resize((180, 150), Image.Resampling.LANCZOS)
                                self.current_photo = ImageTk.PhotoImage(img)
                                self.photo_label.config(image=self.current_photo, text="")
                            except:
                                self.photo_label.config(image='', text="Image Error")
                        else:
                            self.photo_label.config(image='', text="No Photo")

                    # Load Logs
                    self.history_table.delete(*self.history_table.get_children())
                    cur.execute("SELECT time_out, fetcher_name, location FROM history_log WHERE student_id = %s ORDER BY time_out DESC LIMIT 10", (student_id,))
                    for log in cur.fetchall():
                        ts = log[0].strftime("%m/%d %I:%M%p") if log[0] else "N/A"
                        self.history_table.insert("", "end", values=(ts, log[1], log[2]))
        except Exception as e:
            print("Load Details Error:", e)

    def check_for_updates(self):
        try:
            with db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id, student_name, time_out FROM history_log WHERE teacher = %s ORDER BY id DESC LIMIT 1", (self.real_teacher_name,))
                    new_log = cur.fetchone()
                    if new_log:
                        log_id, s_name, t_out = new_log
                        if self.last_log_id is not None and log_id > self.last_log_id:
                            self.notify_teacher(s_name, t_out)
                            self.refresh_tables()
                        self.last_log_id = log_id
        except: pass
        self.after(5000, self.check_for_updates)

    def notify_teacher(self, student_name, time_out):
        messagebox.showinfo("Student Fetched", f"🔔 {student_name} picked up!\nTime: {time_out}")