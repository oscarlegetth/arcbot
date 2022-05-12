from random import randint, random
from functools import partial

def random_coordinate(**kwargs):
    def random_coordinate_number(mult):
        coord = str(random()*mult)
        if len(coord) < 9:
            coord += "0" * (9 - len(coord))
        return coord[0:9]
        
    NS = ["N", "S"][randint(0, 1)]
    WE = ["W", "E"][randint(0, 1)]
    NS_float = random_coordinate_number(90)
    WE_float = random_coordinate_number(180)
    return f"{NS} {NS_float}, {WE} {WE_float}"

def timeout_user(db, username, time):
    db.insert_timeout(username, time)
    return f"/timeout {username} {time}"

options = {
    "30 second timeout" : partial(timeout_user, time=30),
    "1 minute timeout" : partial(timeout_user, time=60),
    "2 minute timeout" : partial(timeout_user, time=120),
    "11 LaughHards" : "LaughHard " * 11,
    "Nothing" : "This space is intentionally left blank",
    "Stache" : "https://gyazo.com/e5077b47aac7662320b523068db30399",
    "4 KEKWs" : "KEKW " * 4,
    "73 CowJAMs" : ["CowJAM " * 50, "CowJAM " * 23],
    "Mind goblin" : "Mind goblin deez nuts! LaughHard",
    "Compliment" : "You look very handsome today, <user>! peepoShy",
    "Apple" : "🍎",
    "A random cooordinate" : random_coordinate
}

class Wheel():

    def __init__(self) -> None:
        self.db = None

    def spin(self, username):
        messages = []
        messages.append(f"{username} has spun the wheel! They win a brand new...")
        rand_idx = randint(0, len(options) - 1)
        reward_name, reward_content = list(options.items())[rand_idx]
        messages.append(f"{reward_name} !!! Pog")
        if type(reward_content) is list:
            for s in reward_content:
                messages.append(self.insert_username(s, username))
        elif callable(reward_content):
            messages.append(reward_content(db=self.db, username=username))
        else:
            messages.append(self.insert_username(reward_content, username))

        self.db.increment_spin_record(username, reward_name, 1)
        return messages
    
    def insert_username(self, s, username):
        return s.replace("<user>", username)
