import sqlite3
from typing import get_args

class DB():


    def __init__(self, ) -> None:
        self.con = sqlite3.connect("ArcBot/records.sqlite3")
        self.cur = self.con.cursor()
        self.con.row_factory = sqlite3.Row

    def reset_db(self):
        with open("init_db.sql") as file:
            self.cur.executescript(file.read())

    def fetched_as_dict(self, fetced):

        return [tuple[0] for tuple in self.cur.description]

    def get_record(self, username, record_name):
        self.cur.execute("SELECT * \
            FROM records \
            WHERE username = ? \
            AND record_name = ?", (username, record_name))

        fetched = self.cur.fetchone()
        if not fetched:
            return None
        else:
            return fetched["val"]
    
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


    def get_spin_record(self, username, record_name):
        self.cur.execute("SELECT * \
            FROM spin_records \
            WHERE username = ? \
            AND record_name = ?", (username, record_name))

        fetched = self.cur.fetchone()
        if not fetched:
            return None
        else:
            return fetched["val"]

    def get_top_spin_records(self, record_name, limit):
        self.cur.execute("SELECT * \
            FROM spin_records \
            WHERE record_name = ? \
            ORDER BY val \
            LIMIT ? ", (record_name, limit))

        fetched = self.cur.fetchall()
        return [(row["username"], row["val"]) for row in fetched]

    def get_top_timeouts_from_spins(self, username=None):
        if username:
            self.cur.execute("SELECT * \
                FROM spin_records \
                WHERE username = ? \
                AND record_name LIKE \"timeout\" \
                ORDER BY val", (username,))
        else:
            self.cur.execute("SELECT * \
                FROM spin_records \
                WHERE record_name LIKE \"timeout\" \
                ORDER BY val \
                LIMIT 5 ")

        return self.cur.fetchall()

    def update_spin_record(self, username, record_name, value):
        current_record = self.get_record(username, record_name)
        if current_record:
            self.cur.execute("UPDATE spin_records \
                SET val = ? \
                WHERE username = ? \
                AND record_name = ?", (value, username, record_name))
        else:
            self.cur.execute("INSERT INTO spin_records \
                VALUES (?, ?, ?)", (username, record_name, value))
        
        self.con.commit()

    def increment_spin_record(self, username, record_name, value):
        current_record = self.get_record(username, record_name)
        if current_record:
            self.cur.execute("UPDATE spin_records \
                SET val = ? \
                WHERE username = ? \
                AND record_name = ?", (current_record + value, username, record_name))
        else:
            self.cur.execute("INSERT INTO spin_records \
                VALUES (?, ?, ?)", (username, record_name, value))

        self.con.commit()
