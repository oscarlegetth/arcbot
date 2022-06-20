import db

class Ship():
    def get_ship(db: db.DB, username):
        return Ship.from_sqlite3_row(db.get_ship_stats(username))

    class Stats():
        def __init__(self):
            self.hp = 10
            self.hull = 1
            self.cannons = 0
            self.sails = 1
            self.cargo_current_amount = 0
            self.cargo_capacity = 2
            self.crew_current_amount = 0
            self.crew_capacity = 4

        def from_sqlite3_row(db_data):
            ship = Ship()
            ship.hp = db_data["hp"]
            ship.hull = db_data["hull"]
            ship.cannons = db_data["cannons"]
            ship.sails = db_data["sails"]
            ship.cargo_current_amount = db_data["cargo_current_amount"]
            ship.cargo_capacity = db_data["cargo_capacity"]
            ship.crew_current_amount = db_data["crew_current_amount"]
            ship.crew_capacity = db_data["crew_capacity"]

    def from_sqlite3_row(db_data):
        return Ship(Ship.Stats.from_sqlite3_row(db_data))

    def __init__(self, stats = None):
        if not stats:
            self.stats = self.Stats()
        else:
            self.stats = stats
    
    def save_ship(self, db: db.DB):
        db.insert_ship(self.username, self.stats)

    