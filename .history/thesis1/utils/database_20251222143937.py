import mysql.connector

def db_connect():
    return mysql.connector.connect(
        host="l",
        user="root",
        password="johnjohn6581506",
        database="rfid_system"
    )
