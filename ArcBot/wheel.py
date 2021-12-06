from random import randint
from typing import List

options = {
    "30 second timeout" : "/timeout <user> 30",
    "1 minute timeout" : "/timeout <user> 60",
    "2 minute timeout" : "/timeout <user> 120",
    "11 LaughHards" : "LaughHard " * 11,
    "Nothing" : "This space is intentionally left blank",
    "Stache" : "https://gyazo.com/e5077b47aac7662320b523068db30399",
    "4 KEKWs" : "KEKW " * 4,
    "73 CowJAMs" : ["CowJAM " * 50, "CowJAM " * 23],
    "Mind goblin" : "Mind goblin deez nuts! LaughHard",
    "Compliment" : "You look very handsome today, <user>! peepoShy",
    "Apple" : "🍎",
}

class Wheel():

    def spin(self, username):
        messages = []
        messages.append(f"{username} has spun the wheel! They win a brand new...")
        rand_idx = randint(0, len(options) - 1)
        reward_name, reward_content = list(options.items())[rand_idx]
        messages.append(f"{reward_name} !!! Pog")
        if type(reward_content) is list:
            for s in reward_content:
                messages.append(self.insert_username(s, username))
        else:
            messages.append(self.insert_username(reward_content, username))
        return messages
    
    def insert_username(self, s, username):
        return s.replace("<user>", username)
