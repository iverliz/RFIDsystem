import mysql.connector
import tkinker

# Change these with your MySQL credentials
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "rfidsystem_db"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INT AUTO_INCREMENT PRIMARY KEY,
        rfid VARCHAR(255) UNIQUE,
        fetcher_name VARCHAR(255),
        address VARCHAR(255),
        contact VARCHAR(255),
        student_id VARCHAR(255),
        student_name VARCHAR(255),
        grade VARCHAR(255),
        teacher VARCHAR(255)
    )
    """)
    conn.commit()
    conn.close()

def insert_record(data):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
    INSERT INTO records 
    (rfid, fetcher_name, address, contact, student_id, student_name, grade, teacher)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, data)
    conn.commit()
    conn.close()

def fetch_all():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM records")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_record(data):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
    UPDATE records SET
        fetcher_name=%s,
        address=%s,
        contact=%s,
        student_id=%s,
        student_name=%s,
        grade=%s,
        teacher=%s
    WHERE rfid=%s
    """
    cursor.execute(sql, data)
    conn.commit()
    conn.close()

def delete_record(rfid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM records WHERE rfid=%s", (rfid,))
    conn.commit()
    conn.close()

def load_table(self):
    self.table.delete(*self.table.get_children())
    for row in fetch_all():
        # Skip ID column, display rest
        self.table.insert("", "end", values=row[1:])
def add_record(self):
    data = (
        self.rfid_var.get(),
        self.name_var.get(),
        self.address_var.get(),
        self.contact_var.get(),
        self.student_id_var.get(),
        self.student_name_var.get(),
        self.grade_var.get(),
        self.teacher_var.get()
    )
    try:
        insert_record(data)
        self.load_table()
        self.clear_fields()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def edit_record(self):
    data = (
        self.name_var.get(),
        self.address_var.get(),
        self.contact_var.get(),
        self.student_id_var.get(),
        self.student_name_var.get(),
        self.grade_var.get(),
        self.teacher_var.get(),
        self.rfid_var.get()
    )
    update_record(data)
    self.load_table()
    self.clear_fields()

def delete_record(self):
    if self.rfid_var.get():
        delete_record(self.rfid_var.get())
        self.load_table()
        self.clear_fields()
