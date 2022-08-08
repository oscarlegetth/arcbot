from code import compile_command
import sqlite3
import os


class DB():
    def __init__(self, ) -> None:
        self.con = sqlite3.connect(os.environ["DATABASE_FILEPATH"])
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()
        # ensure that the database is set up correctly
        self.init_db()

    def init_db(self):
        with open("ArcBot/init_db.sql") as file:
            self.cur.executescript(file.read())

    # general records

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

    # spin records


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

    # arc commands
    def get_arc_command(self, command_name):
        self.cur.execute("SELECT * \
            FROM commands \
            WHERE command_name = ?", (command_name,))
        fetched = self.cur.fetchone()
        if not fetched:
            return None
        else:
            return fetched["command_output"]

    def update_arc_command(self, command_name, command_output):
        self.cur.execute("INSERT INTO commands(command_name, command_output) VALUES (?, ?) \
            ON CONFLICT(command_name) DO UPDATE SET command_output = ? \
            WHERE command_name = ?", (command_name, command_output, command_output, command_name))
        self.con.commit()

    def delete_arc_command(self, command_name):
        self.cur.execute("DELETE FROM commands \
            WHERE command_name = ?", (command_name,))
        self.con.commit()

    def get_all_commands(self):
        self.cur.execute("SELECT * \
            FROM commands")
        fetched = self.cur.fetchall()
        if not fetched:
            return None
        else:
            result = {}
            for row in fetched:
                result[row["command_name"]] = row["command_output"]
            return result

    def get_arcbot_command_info(self, command_name):
        self.cur.execute("SELECT * FROM commands \
            WHERE command_name = ?", (command_name))
        fetched = self.cur.fetchone()
        if not fetched:
            return None
        else:
            return fetched

    def increment_arcbot_command_used(self, command_name, amount):
        current_amount = self.get_arcbot_command_info()["number_of_times_used"]
        if current_amount:
            current_amount = current_amount + amount
            self.cur.execute("UPDATE commands \
                SET number_of_times_used = ? \
                WHERE command_name = ?", (current_amount, command_name))
        self.con.commit()
        return current_amount


    
    # seaman

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

    # coin gambling

    def get_coins(self, username):
        self.cur.execute("SELECT * \
            FROM coins \
            WHERE username = ? ", (username,))

        fetched = self.cur.fetchone()
        if not fetched:
            return "0"
        else:
            return fetched["val"]

    def update_coins(self, username, coins):
        self.cur.execute("INSERT INTO coins(username, val) VALUES (?, ?) \
            ON CONFLICT(username) DO UPDATE SET val=? \
            WHERE username = ?", (username, coins, coins, username))
        self.con.commit()

    def add_coins(self, users, amount):
        user_list = [(u, amount, amount, u) for u in users]
        self.cur.executemany("INSERT INTO coins(username, val) VALUES (?, ?) \
            ON CONFLICT(username) DO UPDATE SET val=val+? \
            WHERE username = ?", (user_list))

        self.con.commit()

    def get_top_coins(self):
        self.cur.execute("SELECT * \
            FROM coins \
            ORDER BY val DESC \
            LIMIT 10")
        
        return self.cur.fetchall()
        
    # hcim death bets
    def insert_hcim_bet(self, username, bet):
        self.cur.execute("INSERT INTO hcim_bets(username, bet) VALUES (?, ?) \
            ON CONFLICT(username) DO UPDATE SET bet=? \
            WHERE username = ?", (username, bet, bet, username))
        self.con.commit()

    def get_hcim_bet(self, username):
        self.cur.execute("SELECT * \
            FROM hcim_bets \
            WHERE username = ? ", (username,))

        fetched = self.cur.fetchone()
        if not fetched:
            return None
        else:
            return fetched["bet"]


    #sailing
    def get_ship_stats(self, username):
        self.cur.execute("SELECT * \
            FROM ships \
            WHERE username = ?", (username,))

        return self.cur.fetchone()

    def insert_ship(self, username, stats):
        # this can surely be done in some better way, but oh well
        self.cur.execute("INSERT INTO hcim_bets(username, hp, hull, cannons, sails, cargo_current_amount, cargo_capacity, crew_current_amount, crew_capacity) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) \
            ON CONFLICT(username) DO UPDATE SET hp = ?, hull = ?, cannons = ?, sails = ?, cargo_current_amount = ?, cargo_capacity = ?, crew_current_amount = ?, crew_capacity  = ? \
            WHERE username = ?", (username, stats.hp, stats.hull, stats.cannons, stats.sails, stats.cargo_current_amount, stats.cargo_capacity, stats.crew_current_amount, stats.crew_capacity, 
            stats.hp, stats.hull, stats.cannons, stats.sails, stats.cargo_current_amount, stats.cargo_capacity, stats.crew_current_amount, stats.crew_capacity, stats.bet, stats.username))
        
        self.con.commit()
