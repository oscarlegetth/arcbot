from datetime import datetime
import os
import re
from asyncio.tasks import sleep
from threading import Timer
from dotenv import load_dotenv
import random
import dotenv

import pkg_resources

from osrsbox import items_api
import twitchio
from twitchio.ext import commands, pubsub, routines
from twitchio.message import Message
import asyncio
import requests

from sailing import Sailing
from hcim_bets import HCIM_bets
from gamble import Gamble
import db

import wheel
import sys

# pip packages: twitchio, osrsbox, websocket, asyncio, dotenv
# made with code from
# https://dev.to/ninjabunny9000/let-s-make-a-twitch-bot-with-python-2nd8

# global objects

if len(sys.argv) > 1:
    dotenv_path = sys.argv[1]
else:
    dotenv_path = ".env"

load_dotenv(dotenv_path=dotenv_path)
items = items_api.load()
wheel = wheel.Wheel()
sailing = Sailing()
pubsub_client = twitchio.Client(token=os.environ['PUBSUB_ACCESS_TOKEN'])
pubsub_client.refresh_token = os.environ['PUBSUB_REFRESH_TOKEN']
pubsub_client.pubsub = pubsub.PubSubPool(pubsub_client)
cogs = {"Sailing" : Sailing, "Gamble" : Gamble, "HCIM_bets" : HCIM_bets}
stream_live = False
running_routines : dict[str, routines.Routine] = {}

# helper methods

def get_random_item():
    return items[random.randint(0, len(items))].name

def get_random_items(i):
    return list(set([get_random_item() for _ in range(i)]))

def get_current_time_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class ArcBot(commands.Bot):

    def __init__(self):
        validate_response = self.validate_token('ACCESS_TOKEN')
        if "expires_in" not in validate_response:
            expires_in = 0
        else:
            expires_in = int(validate_response["expires_in"])

        if expires_in == 0:
            self.refresh_token("ACCESS_TOKEN", "REFRESH_TOKEN")
            
        validate_response = self.validate_token('PUBSUB_ACCESS_TOKEN')
        if "expires_in" not in validate_response:
            self.refresh_token("PUBSUB_ACCESS_TOKEN", "PUBSUB_REFRESH_TOKEN")

        # asyncio.run(self.refresh_and_connect_access_token(delay=expires_in - 15))
        # print(f"set up timer to refresh access token in {expires_in} seconds")

        print(f"Creating bot instance")
        super().__init__(token=os.environ['ACCESS_TOKEN'], 
            client_id=os.environ['CLIENT_ID'], 
            nick=os.environ['BOT_NICK'], 
            prefix=os.environ['BOT_PREFIX'], 
            initial_channels=[os.environ['CHANNEL']])
        print(f"Connected to twitch API")

        self.db = db.DB()
        wheel.db = self.db
        sailing.db = self.db
        sailing.bot = self
        self.arcbot_commands = self.db.get_all_commands()
        if not self.arcbot_commands:
            self.arcbot_commands = {}
        else:
            print(f"Loaded {len(self.arcbot_commands)} command(s) from database")
        self.chatters_cache = []
        self.known_bots = [os.environ["BOT_NICK"], "creatisbot", "nightbot", "anotherttvviewer", "streamlabs", "kaxips06", "7tvapp"]
        self.announcements = []
        for announcement in self.db.get_all_announcements():
            self.announcements.append(announcement["announcement_text"])
        self.next_announcements_index = 0

        for default_cog in os.environ["DEFAULT_COGS"].split(" "):
            self.add_cog(cogs[default_cog](self))
        print(f"Successfully added cogs")

    async def run_pubsub(self):
        validate_response = self.validate_token("PUBSUB_ACCESS_TOKEN")
        await asyncio.sleep(1)
        if "expires_in" not in validate_response:
            expires_in = 0
        else:
            expires_in = int(validate_response["expires_in"])
        asyncio.create_task(self.refresh_and_connect_to_pubsub(expires_in))
        print(f"set up timer to refresh pubsub access token in {expires_in} seconds")

        try:
            await self.connect_pubsub()
            await asyncio.sleep(1)
        except (twitchio.errors.AuthenticationError):
            print("Failed to connect to pubsub server, attempting to refresh token")
            self.refresh_token("PUBSUB_ACCESS_TOKEN", "PUBSUB_REFRESH_TOKEN")
            try:
                await self.connect_pubsub()
            except (twitchio.errors.AuthenticationError):
                print("Failed to connect to pubsub server after token refresh, aborting pubsub connection")
        if pubsub_client._connection.is_alive:
            print("Connected to pubsub server")
        else:
            print("Failed to connect to pubsub server, but token was valid?!")

    async def connect_pubsub(self):
        topics = [
            pubsub.channel_points(os.environ['PUBSUB_ACCESS_TOKEN'])[int(os.environ['CHANNEL_ID'])]
        ]
        await pubsub_client.pubsub.subscribe_topics(topics)
        await pubsub_client.connect()

    async def event_ready(self):
        """Called once when the bot goes online."""
        print(f"event_ready called")
        await self.connect_pubsub()
        self.master_routine.start()
        version = pkg_resources.get_distribution('ArcBot').version
        message = f"{os.environ['BOT_NICK']} v{version} is online!"
        # ---------------------------------------------------
        self.announce_routine.start()
        print(message)
        self.send_message(message)

    def refresh_token(self, token_key : str, refresh_token_key : str):
        # send http request for a new token
        url = "https://id.twitch.tv/oauth2/token"
        payload = f"grant_type=refresh_token&refresh_token={os.environ[refresh_token_key]}&client_id={os.environ['CLIENT_ID']}&client_secret={os.environ['CLIENT_SECRET']}"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            print(f"Successfully refreshed {token_key}")
        else:
            print(f"Could not refresh {token_key}. Response code: {response.status_code}")
            print(f"Full response: {response.text}")
            return

        new_access_token = response.json()['access_token']
        expires_in = int(response.json()['expires_in'])
        refresh_token = response.json()['refresh_token']

        dotenv.set_key(dotenv_path, token_key, new_access_token)
        dotenv.set_key(dotenv_path, refresh_token_key, refresh_token)
        load_dotenv(override=True)
        return expires_in

    def validate_token(self, token_key : str):
        print(f"Validating {token_key}")
        url = "https://id.twitch.tv/oauth2/validate"
        headers = {"Authorization" : f"Bearer {os.environ[token_key].replace('oauth:', '')}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(f"Successfully validated {token_key}. HTTP 200.")
        return response.json()

    async def refresh_and_connect_to_pubsub(self, delay : int = 0):
        await asyncio.sleep(delay)
        expires_in = self.refresh_token("PUBSUB_ACCESS_TOKEN", "PUBSUB_REFRESH_TOKEN")
        await self.connect_pubsub()
        await asyncio.create_task(self.refresh_and_connect_to_pubsub(delay=expires_in - 15))

    async def refresh_and_connect_access_token(self, delay : int = 0):
        await asyncio.sleep(delay)
        expires_in = self.refresh_token("ACCESS_TOKEN", "REFRESH_TOKEN")
        # self._connection._token = os.environ["ACCESS_TOKEN"]

        _ = os.environ["ACCESS_TOKEN"]
         
        await self.connect()
        await asyncio.create_task(self.refresh_and_connect_access_token(delay=expires_in - 15))

    async def event_command_error(self, context: commands.Context, error: Exception) -> None:
        if type(error) is twitchio.ext.commands.errors.CommandNotFound:
            return None
        else:
            await super().event_command_error(context, error)

    #------------------------------------
    # HELPER FUNCTIONS
    #------------------------------------

    def send_message(self, message):
        chan = self.get_channel(os.environ["CHANNEL"][1:])
        loop = asyncio.get_event_loop()
        loop.create_task(chan.send(message))

    def remove_7tv_chars(self, message):
        weird_7tv_chars = " 󠀀 󠀀" # weird characters added at the end of messages by 7tv, not just spaces!
        return  message.strip(weird_7tv_chars)

    def get_random_user(self, ctx):
        chatters_list = [chatter.name for chatter in list(ctx.chatters) if chatter.name not in self.known_bots]
        return chatters_list[random.randint(0, len(chatters_list)) - 1]

    def check_if_mod(self, user):
        return "moderator" in user.badges or "broadcaster" in user.badges

    def check_if_stream_live(self):
        url = "https://api.twitch.tv/helix/streams"
        payload = f"user_login={os.environ['CHANNEL']}"
        headers = {"Authorization": f"Bearer {os.environ['ACCESS_TOKEN']}",
            "Client-Id": f"{os.environ['CLIENT_ID']}"}
        response = requests.post(url, data=payload, headers=headers)
        json = response.json()
        if "data" in json and len(json["data"]) > 0:
            return json["data"][0]["type"] == "live"
        return False



    #------------------------------------
    # NON-COMMANDS
    #------------------------------------

    async def event_message(self, ctx):
        """Runs every time a message is sent in chat."""
        if type(ctx) is Message:
            if not ctx.author:
                return
            # make sure the bot ignores itself
            if ctx.author and ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
                return

            ctx.content = self.remove_7tv_chars(ctx.content)
            message = self.remove_7tv_chars(ctx.content)
            lower_message = message.lower()
            # respond to messages ending with "er?"
            if message[-3:] == "er?" and (random.randint(0, 9) == 0 or "broadcaster" in ctx.author.badges):
                self.send_message(f"{message.split()[-1]} I hardly know her!!! LaughHard")

            # respond to messages starting with "i'm"
            if message.find(" ") != -1 and (message[0:2] == "im" or message[0:3] == "i\'m") and (random.randint(0, 19) == 0 or "broadcaster" in ctx.author.badges):
                end_index = next((i for i, ch in enumerate(message) if ch in {'.',',','!','?'}),None)
                start_index = message.find(" ")
                self.send_message(f"hi {message[start_index + 1:end_index]}, i'm {os.environ['BOT_NICK']}")
            # respond to people calling the bot stupid
            if lower_message[0:10] == "stupid bot":
                self.send_message(f"{ctx.author.name} is a stupid human 😡")

            if lower_message[0:8] == "good bot":
                self.send_message(f"{ctx.author.name} is a good human peepoShy")

            # respond to bastin
            if ctx.author.name.lower() == "bastin101" and random.randint(0, 3) == 0:
                random_number = random.randint(0, 101)
                self.send_message(f"bastin{random_number}+{101 - random_number} KEKW")

            # respond to commands in db
            command_name = message.split(" ", 1)[0]
            if command_name in self.arcbot_commands:
                output = self.process_arcbot_command(ctx, command_name, self.arcbot_commands[command_name])
                if output:
                    self.send_message(output)

        else:
            print(f"Unexpected context encountered. Type: {type(ctx)} str: {str(ctx)}")

        self.chatters_cache = (await bot.get_context(ctx)).chatters
        await self.handle_commands(ctx)

    #------------------------------------
    # COMMANDS
    #------------------------------------

    @commands.command(name='test')
    async def test(self, ctx: commands.Context):
        """Adds a '!test' command to the bot."""
        await ctx.send('test passed!')

    @commands.command(name="random_item")
    async def random_item(self, ctx: commands.Context):
        await ctx.send(get_random_item())

    rare_spank_table = ["WooxSolo", "Odablock", "Framed", "J1mmy", "Faux", "Coxie", "Mmorpg", "Real_Matk", "SkillSpecs", "Mr_Mammal", "Alfie", "Roidie", "itswill", "SkiddlerRS", "Dino_xx", "JagexModAsh", "FBI_Survelliance_Van_381b"]

    @commands.command(name="bye")
    async def bye(self, ctx: commands.Context):
        await ctx.send(f"/timeout {ctx.author.name} 1")

    @commands.command(name="cog")
    async def toggle_cog(self, ctx: commands.Context):
        if not self.check_if_mod(ctx.author):
            await ctx.reply(f"You are not a moderator.")
            return

        args = ctx.message.content.split(" ")[1:]
        if len(args) == 0:
            await ctx.reply(f"Available cogs are: {', '.join([s for s in cogs.keys()])}")
            return

        if args[0] == "enabled":
            await ctx.reply(f"Currently enabled cogs are: {', '.join(bot._cogs.keys())}")
            return

        if len(args) < 2:
            await ctx.reply(f"Usage: '!cog <enable/disable> <cog_name>' to enable/disable cogs, '!cog enabled' to see currently enabled cogs")
            return

        cog_name = args[1]
        if cog_name not in cogs.keys():
            await ctx.reply(f"Cog '{cog_name}' not found, available cogs are: {', '.join(cogs.keys())}")
            return

        if args[0] == "enable":
            if bot.get_cog(cog_name):
                await ctx.reply(f"Cog '{cog_name}' is already enabled.")
                return
            else:
                bot.add_cog(cogs[cog_name](self))
                await ctx.reply(f"Cog '{cog_name}' enabled.")
                return

        if args[0] == "disable":
            if not bot.get_cog(cog_name):
                await ctx.reply(f"Cog '{cog_name}' is already disabled.")
                return
            else:
                bot.remove_cog(cog_name)
                await ctx.reply(f"Cog '{cog_name}' disabled.")
                return

        await ctx.reply(f"Usage: !cog <enable/disable> <cog_name>")

    #------------------------------------
    # ARCBOT-COMMANDS
    #------------------------------------

    @commands.command(name="addarccom")
    async def add_arcbot_command(self, ctx: commands.Context):
        if not self.check_if_mod(ctx.author):
            return
        args = ctx.message.content.split(" ", 2)
        if len(args) < 3:
            await ctx.reply(f"Usage: !{args[0]} [command name] [command output]. Use !helparccom for more info about the syntax.")
            return
        command_name = args[1]
        command_output = args[2]
        self.db.update_arc_command(command_name, command_output, ctx.author.name, get_current_time_str())
        self.arcbot_commands[command_name] = command_output
        await ctx.reply(f"Command successfully added")

    @commands.command(name="editarccom")
    async def edit_arcbot_command(self, ctx: commands.Context):
        await self.add_arcbot_command(ctx)

    @commands.command(name="delarccom")
    async def delete_arcbot_command(self, ctx: commands.Context):
        if not self.check_if_mod(ctx.author):
            return
        args = ctx.message.content.split(" ", 1)
        command_name = args[1]
        if len(args) < 2:
            await ctx.reply(f"Usage: !delarccom [command name]")
            return
        elif command_name in self.arcbot_commands:
            self.db.delete_arc_command(command_name)
            del self.arcbot_commands[command_name]
            await ctx.reply(f"Command successfully deleted")
        else:
            await ctx.reply(f"Command {command_name} is not a command")

    @commands.command(name="helparccom")
    async def show_help_arcbot_command(self, ctx: commands.Context):
        await ctx.reply(f"Use !addarccom to add or edit a command. !delarccom deletes a command. \
            Special strings: $(user) user who uses command, \
            $(target) first word after command, \
            $(random user) a random chatter, \
            $(random) a random number 0-100, \
            $(random x) a random number 0-x. \
            $(count) the number of times this command has been used")
    
    @commands.command(name="infoarccom")
    async def show_info_arcbot_command(self, ctx: commands.Context):
        args = ctx.message.content.split(" ")
        if len(args) < 2:
            await ctx.reply("Usage: !infoarccom [command name]")
            return
        command_name = args[1]
        command_info = self.db.get_arcbot_command_info(command_name)
        if not command_info:
            await ctx.reply(f"Command {command_name} not found")
            return
        await ctx.reply(f"Command {command_name}: Has been used {command_info['number_of_times_used']} time{'' if command_info['number_of_times_used'] == 1 else 's'}. Created by {command_info['added_by']} at {command_info['added_at']}.")

    def process_arcbot_command(self, ctx: commands.Context, command_name: str, command_output: str) -> str:
        """
        Replaces all occurances of '$(user)' with the name of the user who issued the command \n
        Replaces all occurances of '$(target)' with whatever first word is written after the name of the command \n
        Replaces all occurances of '$(random user)' with a random user from the chatters_cache \n
        Replaces all occurances of '$(random)' with a random number between 0-100 \n
        Replaces all occurances of '$(random x)' with a random number between 0-x \n
        Replaces all occurances of '$(count)' with the number of times this command has been used \n
        """
        self.db.increment_arcbot_command_used(command_name, 1)
        def randint_replace(matchobj):
            return str(random.randint(0, int(matchobj.groups()[1])))

        command_output = command_output.replace("$(user)", ctx.author.name)
        args = ctx.content.split(" ", 2)
        if type(args) is list and len(args) >= 2:
            command_output = command_output.replace("$(target)", args[1])
        else:
            command_output = command_output.replace("$(target)", "")
        if len(self.chatters_cache) > 0:
            command_output = command_output.replace("$(random user)", str(random.choice(tuple(self.chatters_cache)).name))
        else:
            command_output = command_output.replace("$(random user)", ctx.author.name)
        command_output = command_output.replace("$(random)", str(random.randint(0, 100)))
        command_output = re.sub(r"\$\((random) (\d+)\)", randint_replace, command_output)
        command_output = command_output.replace("$(count)", str(self.db.get_arcbot_command_info(command_name)["number_of_times_used"]))
        return command_output

    #------------------------------------
    # ANNOUNCEMENTS
    #------------------------------------

    @commands.command(name="addannouncement")
    async def add_announcement(self, ctx: commands.Context):
        announcement_to_add = ctx.message.content.split(" ", 1)
        if announcement_to_add:
            self.announcements.append(announcement_to_add)
            self.db.insert_announcement(announcement_to_add, ctx.author.name, get_current_time_str())
            await ctx.reply(f"Announcement added.")
        else:
            await ctx.reply(f"Usage: !addannouncement [announcement text]")

    @commands.command(name="viewannouncements")
    async def view_announcements(self, ctx: commands.Context):
        await ctx.author.send(f"Current announcements:")
        for i, announcement in enumerate(self.announcements):
            await ctx.author.send(f"{i}: {announcement}")
            await sleep(0.5)
        await ctx.reply(f"Sent list of announcements")

    #------------------------------------
    # CHANNEL POINT REDEMPTIONS
    #------------------------------------

    @pubsub_client.event()
    async def event_pubsub_channel_points(event: pubsub.PubSubChannelPointsMessage):
        title = event.reward.title.lower()
        if title == "add a seaman to the arc":
            new_amount = bot.db.insert_seaman(1)
            bot.send_message(f"Thank you for adding more seamen to the arc. The arc now has {new_amount} seamen peepoMayo")
            
        elif title == "spin the arcwheel":
            username = event.user.name
            result = wheel.spin(username)
            for s in result:
                await sleep(1)
                bot.send_message(s)

        elif title == "rng timeout":
            target = event.input.split()[0].lower()
            if target[0] == '@':
                target = target[1:]
            bot.send_message(f"{event.user.name} is trying to timeout {target} PauseChamp")
            await sleep(2)
            if random.randint(0, 1) == 0:
                bot.send_message(f"{target} has been harvested for 5 minutes x0r6ztGiggle")
                bot.send_message(f"/timeout {target} 5m")
            else:
                if random.randint(0, 1) == 0:
                    bot.send_message(f"{target} managed to parry the timeout! {event.user.name} has been timed out for 5 minutes instead.")
                    bot.send_message(f"/timeout {event.user.name} 5m")
                else:
                    bot.send_message(f"{target} gets to live to see another day")

        elif title == "song request":
            bot.send_message("song requested pogg")

    #------------------------------------
    # ROUTINES
    #------------------------------------

    @routines.routine(minutes=10)
    async def master_routine(self):
        """
        Master routine. Stops all other routines when the stream is not live and resumes then when the stream goes live again.
        """
        if os.environ["PUBSUB_ACCESS_TOKEN"] != pubsub_client._connection._token:
            dotenv.set_key(dotenv_path,  "PUBSUB_ACCESS_TOKEN", pubsub_client._connection._token)
            load_dotenv(override=True)
        # if os.environ["PUBSUB_REFRESH_TOKEN"] != pubsub_client.refresh_token:
        #     dotenv.set_key(dotenv_path,  "PUBSUB_REFRESH_TOKEN", pubsub_client.refresh_token)
        if os.environ["ACCESS_TOKEN"] != self._connection._token:
            dotenv.set_key(dotenv_path,  "ACCESS_TOKEN", self._connection._token)
            load_dotenv(override=True)
        # if os.environ["REFRESH_TOKEN"] != self.refresh_token:
        #     dotenv.set_key(dotenv_path,  "PUBSUB_REFRESH_TOKEN", self.refresh_token)

        routines = [self.sailing_routine, self.announce_routine]
        if self.check_if_stream_live():
            stream_live = True
            for routine in routines:
                if routine.__name__ not in running_routines:
                    routine.start()
                    running_routines[routine.__name__] = routine
        else:
            stream_live = False
            for routine in running_routines.values():
                routine.stop()

    @routines.routine(seconds=10)
    async def announce_routine(self):
        if len(self.announcements) == 0:
            return
        announcement = self.announcements[self.next_announcements_index]
        self.next_announcements_index += 1
        if self.next_announcements_index >= len(self.announcements):
            self.announcements = 0
        self.send_message(f"/announcement {announcement}")

    @routines.routine(seconds=10)
    async def sailing_routine(self):
        if "Sailing" in bot.get_cog.keys():
            sailing.update()


if __name__ == "__main__":
    bot = ArcBot()
    bot.run()
