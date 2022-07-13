from time import time
import db

ship_cache = {}

class Ship():
    def get_ship(db: db.DB, username):
        if username in ship_cache:
            return ship_cache[username]
        else:
            ship = Ship.from_sqlite3_row(db.get_ship_stats(username))
            # TODO: remove oldest ship from cache when too many ships are in cache
            ship_cache[username] = ship
            return ship

    class Stats():
        def __init__(self, username):
            self.username = username
            self.hp = 10
            self.hull = 1
            self.cannons = 0
            self.sails = 1
            self.cargo_current_amount = 0
            self.cargo_capacity = 2
            self.crew_current_amount = 0
            self.crew_capacity = 4
            self.time_set_sail = -1

        @classmethod
        def from_sqlite3_row(cls, db_data):
            stats = Ship.Stats()
            stats.username = db_data["username"]
            stats.hp = db_data["hp"]
            stats.hull = db_data["hull"]
            stats.cannons = db_data["cannons"]
            stats.sails = db_data["sails"]
            stats.cargo_current_amount = db_data["cargo_current_amount"]
            stats.cargo_capacity = db_data["cargo_capacity"]
            stats.crew_current_amount = db_data["crew_current_amount"]
            stats.crew_capacity = db_data["crew_capacity"]
            return stats
        
        def stats_to_str(self):
            return f"hp: {self.hp}, \
                hull: {self.hull}, \
                cannons: {self.cannons}, \
                sails: {self.sails}, \
                cargo: {self.cargo_current_amount}/{self.cargo_capacity}, \
                crew: {self.crew_current_amount}/{self.crew_capacity}"

    def from_sqlite3_row(db_data):
        return Ship(Ship.Stats.from_sqlite3_row(db_data))

    def __init__(self, username : str, stats = None):
        if not stats:
            self.stats = self.Stats(username)
        else:
            self.stats = stats
    
    def save_ship(self, db: db.DB):
        db.insert_ship(self.username, self.stats)

    def get_stats_str(self):
        return f"Ship stats: {self.stats.stats_to_str()}"

    def set_sail(self):
        self.stats.time_set_sail = int(time())
