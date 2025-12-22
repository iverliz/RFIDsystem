import mysql.connector

def db_connect():
    return mysql.connector.connect(
        host="12",
        user="root",
        password="johnjohn6581506",
        database="rfid_system"
    )
