def db_connect(self):
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="johnjohn6581506",        # put your MySQL password
        database="rfid_system"
    )
