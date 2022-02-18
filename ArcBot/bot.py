import os
from asyncio.tasks import sleep
from xml.dom.minidom import CharacterData
from dotenv import load_dotenv
from random import randint

import pkg_resources

from osrsbox import items_api
import twitchio
from twitchio.ext import commands, pubsub
from twitchio.message import Message
import asyncio

from sailing import Sailing
from hcim_bets import HCIM_bets
from gamble import Gamble
import db

import wheel
import sys

# pip packages: twitchio, osrsbox, websocket, asyncio, dotenv
# mostly code from
# https://dev.to/ninjabunny9000/let-s-make-a-twitch-bot-with-python-2nd8

# global objects

if len(sys.argv) > 1:
    dotenv_path = sys.argv[1]
else:
    dotenv_path = ".env"

load_dotenv(dotenv_path=dotenv_path)
items = items_api.load()
wheel = wheel.Wheel()
pubsub_client = twitchio.Client(token=os.environ['PUBSUB_ACCESS_TOKEN'])
pubsub_client.pubsub = pubsub.PubSubPool(pubsub_client)
cogs = {"Sailing" : Sailing, "Gamble" : Gamble, "HCIM_bets" : HCIM_bets}

# helper methods

def get_random_item():
    return items[randint(0, len(items))].name

def get_random_items(i):
    return list(set([get_random_item() for _ in range(i)]))

class ArcBot(commands.Bot):

    def __init__(self):
        super().__init__(token=os.environ['TMI_TOKEN'], 
        client_id=os.environ['CLIENT_ID'], 
        nick=os.environ['BOT_NICK'], 
        prefix=os.environ['BOT_PREFIX'], 
        initial_channels=[os.environ['CHANNEL']])
        self.db = db.DB()
        wheel.db = self.db
        self.chatters_cache = []
        self.known_bots = ["arcbot73", "creatisbot", "nightbot", "anotherttvviewer", "streamlabs", "kaxips06"]
        
        for default_cog in os.environ["DEFAULT_COGS"].split(" "):
            self.add_cog(cogs[default_cog](self))


    async def run_pubsub(self):
        topics = [
            pubsub.channel_points(os.environ['PUBSUB_ACCESS_TOKEN'])[int(os.environ['CHANNEL_ID'])]
        ]
        await pubsub_client.pubsub.subscribe_topics(topics)
        await pubsub_client.connect()

    async def event_ready(self):
        """Called once when the bot goes online."""
        asyncio.create_task(self.run_pubsub())
        version = pkg_resources.get_distribution('ArcBot').version
        message = f"{os.environ['BOT_NICK']} v{version} is online!"
        await asyncio.sleep(1)
        print(message)
        self.send_message(message)


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
        return chatters_list[randint(0, len(chatters_list)) - 1]

    def check_if_mod(self, user):
        return "moderator" in user.badges or "broadcaster" in user.badges

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
            # respond to messages ending with "er?"
            if message[-3:] == "er?" and randint(0, 9) == 0:
                self.send_message(f"{message.split()[-1]} I hardly know her!!! LaughHard")

            # respond to people calling the bot stupid
            if message[0:10].lower() == "stupid bot":
                self.send_message(f"{ctx.author.name} is a stupid human 😡")

            if message[0:8].lower() == "good bot":
                self.send_message(f"{ctx.author.name} is a good human peepoShy")

            # respond to bastin
            if ctx.author.name.lower() == "bastin101" and randint(0, 3) == 0:
                random_number = randint(0, 101)
                self.send_message(f"bastin{random_number}+{101 - random_number} KEKW")

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

    @commands.command(name="task")
    async def task(self, ctx: commands.Context):
        if not "moderator" in ctx.author.badges:
            return
        
        if len(ctx.message.content < 6):
            return

        message = ctx.message.content[6:]
        with open("current_task.txt", 'w') as file:
            file.write(f'{message}')
            await ctx.send(f"Task has been updated to: {message}")


    @commands.command(name="random_item")
    async def random_item(self, ctx: commands.Context):
        await ctx.send(get_random_item())

    rare_spank_table = ["WooxSolo", "Odablock", "Framed", "J1mmy", "Faux", "Coxie", "Mmorpg", "Real_Matk", "SkillSpecs", "Mr_Mammal", "Alfie", "Roidie", "itswill", "SkiddlerRS", "Dino_xx", "JagexModAsh", "FBI_Survelliance_Van_381b"]

    @commands.command(name="spank")
    async def spank(self, ctx: commands.Context):
        if randint(0, 99) == 0:
            spanked = self.rare_spank_table[randint(0, len(self.rare_spank_table) - 1)]
        else:
            spanked = self.get_random_user(ctx)

        await ctx.send(f"{ctx.author.name} has spanked {spanked} peepoShy")

    @commands.command(name="slap")
    async def slap(self, ctx: commands.Context):
        
        if randint(0, 99) == 0:
            slapped = self.rare_spank_table[randint(0, len(self.rare_spank_table) - 1)]
        else:
            slapped = self.get_random_user(ctx)

        await ctx.send(f"{ctx.author.name} has slapped {slapped} x0r6ztGiggle")

    @commands.command(name="bye")
    async def bye(self, ctx: commands.Context):
        await ctx.send(f"/timeout {ctx.author.name} 1")

    @commands.command(name="timeouts")
    async def timeouts(self, ctx: commands.Context):
        args = ctx.message.content.split()[1:]
        if len(args) > 0:
            timeouts = self.db.get_top_timeouts(args[0])
            if timeouts:
                await ctx.send(f"{args[0]} has been timed out a total of {timeouts} seconds by the arcwheel")
            else:
                await ctx.send(f"{args[0]} has not yet been timed out by the arcwheel")
        else:
            timeouts = self.db.get_top_timeouts()
            if not timeouts:
                await ctx.send("No one has been timed out yet")
                return
            message = f"Top timeouts:"
            for timeout in timeouts:
                message = message + f"\n{timeout[0]}: {timeout[1]}"
            await ctx.send(message)

    @commands.command(name="cog")
    async def toggle_cog(self, ctx: commands.Context):
        if not self.check_if_mod(ctx.author):
            await ctx.reply(f"You are not a moderator.")
            return

        args = ctx.message.content.split(" ")[1:]
        if len(args) == 0:
            await ctx.reply(f"Available cogs are: {', '.join([s for s in cogs.keys()])}")
            return

        if len(args) < 2:
            await ctx.reply(f"Usage: !cog <enable/disable> <cog_name>")
            return

        cog_name = args[1]
        if cog_name not in cogs.keys():
            await ctx.reply(f"Cog '{cog_name}' not found, available cogs are: {', '.join([s for s in cogs.keys()])}")
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
    # CHANNEL POINT REDEMPTIONS
    #------------------------------------

    @pubsub_client.event()
    async def event_pubsub_channel_points(event: pubsub.PubSubChannelPointsMessage):
        title = event.reward.title.lower()
        if title == "add a seaman to the arc":
            new_amount = bot.db.insert_seaman(1)
            bot.send_message(f"Thank you for adding more seamen to the arc. The arc now has {new_amount} seamen peepoMayo")
            
        elif title == "spin The arcwheel":
            username = event.user.name
            result = wheel.spin(username)
            for s in result:
                await sleep(1)
                bot.send_message(s)

        elif title == "buy ship and crew":
            pass

        elif title == "rng timeout":
            target = event.input.split()[0].lower()
            if target[0] == '@':
                target = target[1:]
            bot.send_message(f"{event.user.name} is trying to timeout {target} PauseChamp")
            await sleep(2)
            if randint(0, 1) == 0:
                bot.send_message(f"{target} has been harvested for 5 minutes x0r6ztGiggle")
                bot.send_message(f"/timeout {target} 5m")
            else:
                if randint(0, 1) == 0:
                    bot.send_message(f"{target} managed to parry the timeout! {event.user.name} has been timed out for 5 minutes instead.")
                    bot.send_message(f"/timeout {event.user.name} 5m")
                else:
                    bot.send_message(f"{target} gets to live to see another day")

if __name__ == "__main__":
    bot = ArcBot()
    bot.run()
