import mysql.connector

def db_connect():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="johnjohn6581506",
        database="rfid_system"
    )
