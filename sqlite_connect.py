import sqlite3
from sqlite3 import Error


class Database:

    def __init__(self, database_name):
        try:
            self.dbname = database_name
            self.conn = sqlite3.connect(f"data_files/database/{self.dbname}.db")
            self.cursor = self.conn
        except Error as e:
            print(e)

    def create_table(self):
        try:
            sql = """CREATE TABLE IF NOT EXISTS RESTORED_MESSAGE(
            SENDER_ID TEXT(10) NOT NULL,
            RECEIVER_ID TEXT(10) NOT NULL,
            MESSAGE TEXT(255) NOT NULL,
            DATE DATETIME default CURRENT_TIMESTAMP);"""

            self.cursor.execute(sql)
            self.cursor.commit()
        except Error as e:
            print(e)

    def insert_data(self, msg_data):
        try:

            sql = """INSERT INTO RESTORED_MESSAGE(SENDER_ID, RECEIVER_ID, MESSAGE) VALUES ('%s', '%s', '%s')"""\
                  % (msg_data['sender'], msg_data['recv'], msg_data['message'])
            self.cursor.execute(sql)
            self.cursor.commit()
            print("success")
        except Error as e:
            self.cursor.rollback()
            print(e)

    def retrieve_data(self, sender_id, reciever_id):
        try:
            sql = "SELECT SENDER_ID, RECEIVER_ID, MESSAGE FROM RESTORED_MESSAGE" \
                  " WHERE (SENDER_ID = %s AND RECEIVER_ID = %s) OR (SENDER_ID = %s AND RECEIVER_ID = %s)" \
                  "ORDER BY DATE ASC" % (sender_id, reciever_id, reciever_id,  sender_id)
            result = self.cursor.execute(sql)

            return result.fetchall()

        except Error as e:
            print(e)