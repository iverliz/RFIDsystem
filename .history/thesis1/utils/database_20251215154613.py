def db_connect(self):
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="johnjohn",        # put your MySQL password
        database="rfid_system"
    )
