import sqlite3

class DB():
    def __init__(self, ) -> None:
        self.con = sqlite3.connect("records.sqlite3")
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()
        # ensure that the database is set up correctly
        self.init_db()

    def init_db(self):
        with open("ArcBot/init_db.sql") as file:
            self.cur.executescript(file.read())

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

    def get_top_timeouts(self, username=None):
        if username:
            self.cur.execute("SELECT * \
                FROM timeouts \
                WHERE username = ? ", (username,))
            
            fetched = self.cur.fetchone()
            if not fetched:
                return None
            else:
                return fetched["val"]
        else:
            self.cur.execute("SELECT * \
                FROM timeouts \
                ORDER BY val DESC \
                LIMIT 5 ")
            fetched = self.cur.fetchall()
            if not fetched:
                return None
            else:
                return [(row["username"], row["val"]) for row in fetched]


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

    def get_timeout(self, username):
        self.cur.execute("SELECT * \
            FROM timeouts \
            WHERE username = ? ", (username,))

        fetched = self.cur.fetchone()
        if not fetched:
            return None
        else:
            return fetched["val"]

    def insert_timeout(self, username, time):
        current_timeout = self.get_timeout(username)
        if current_timeout:
            self.cur.execute("UPDATE timeouts \
                SET val = ? \
                WHERE username = ? ", (current_timeout + time, username))
        else:
            self.cur.execute("INSERT INTO timeouts \
                VALUES (?, ?)", (username, time))

        self.con.commit()

    def get_seaman_amount(self):
        self.cur.execute("SELECT * \
            FROM records \
            WHERE record_name = ? ", ("seaman_amount", ))

        fetched = self.cur.fetchone()
        if not fetched:
            return None
        else:
            return int(fetched["val"])

    def insert_seaman(self, amount):
        current_amount = self.get_seaman_amount()
        if current_amount:
            current_amount = current_amount + amount
            self.cur.execute("UPDATE records \
                SET record_name = ?, \
                val = ?", ("seaman_amount", current_amount))
        else:
            self.cur.execute("INSERT INTO records \
                VALUES (?, ?, ?)", ("", "seaman_amount", 1))
            current_amount = 1

        self.con.commit()
        return current_amount
