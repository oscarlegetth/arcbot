import sqlite3
from typing import get_args

class DB():

    def __init__(self, ) -> None:
        self.con = sqlite3.connect("ArcBot/records.sqlite3")
        self.cur = self.con.cursor()

    def reset_db(self):
        with open("init_db.sql") as file:
            self.cur.executescript(file.read())

    def get_record(self, username, record_name):
        self.cur.execute("SELECT * \
            FROM records \
            WHERE username = ? \
            AND record_name = ?", (username, record_name))

        fetched = self.cur.fetchall()
        if not fetched:
            return None
        else:
            return fetched[0][2]
    
    def update_record(self, username, record_name, value):
        current_record = self.get_record(username, record_name)
        if current_record:
            self.cur.execute("UPDATE records \
                SET val = ? \
                WHERE username = ? \
                AND record_name = ?", (value, username, record_name))
        else:
            self.cur.execute("INSERT INTO records \
                VALUES (?, ?, ?)", (username, record_name, value))

        self.con.commit()
