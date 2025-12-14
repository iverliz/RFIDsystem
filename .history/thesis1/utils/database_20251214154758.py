import mysql.connector

# Change these with your MySQL credentials
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",
    "database": "rfidsystem111_db"
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
