import os
from asyncio.tasks import sleep
import random
from time import time
from dotenv import load_dotenv
from random import randint
import pkg_resources

from osrsbox import items_api
import twitchio
from twitchio.errors import AuthenticationError
from twitchio.ext import commands, pubsub
from twitchio.ext.commands.core import Context, command
from twitchio.message import Message
import asyncio
from twitchio.models import AutomodCheckMessage

from twitchio.user import UserBan
import db

import wheel



# pip packages: twitchio, osrsbox, websocket, asyncio, dotenv
# mostly code from
# https://dev.to/ninjabunny9000/let-s-make-a-twitch-bot-with-python-2nd8

# global objects

load_dotenv()
items = items_api.load()
wheel = wheel.Wheel()
known_bots = ["arcbot73", "creatisbot", "nightbot", "anotherttvviewer", "streamlabs"]
pubsub_client = twitchio.Client(token=os.environ['PUBSUB_ACCESS_TOKEN'])
pubsub_client.pubsub = pubsub.PubSubPool(pubsub_client)

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

    async def run_pubsub(self):
        topics = [
            pubsub.channel_points(os.environ['PUBSUB_ACCESS_TOKEN'])[int(os.environ['CHANNEL_ID'])]
        ]
        await pubsub_client.pubsub.subscribe_topics(topics)
        await pubsub_client.connect()

    async def event_ready(self):
        """Called once when the bot goes online."""
        #asyncio.create_task(self.run_pubsub())
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
        chatters_list = [chatter.name for chatter in list(ctx.chatters) if chatter.name not in known_bots]
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
                self.send_message(f"{ctx.author.name} is a stupid human")

            # respond to bastin
            if ctx.author.name.lower() == "bastin101" and randint(0, 3) == 0:
                random_number = randint(0, 101)
                self.send_message(f"bastin{random_number}+{101 - random_number} KEKW")

        else:
            print(f"Unexpected context encountered. Type: {type(ctx)} str: {str(ctx)}")
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

    # @commands.command(name="random_user")
    # async def random_user(self, ctx: commands.Context):
    #     chatters_list = [chatter.name for chatter in list(ctx.chatters) if chatter.name not in known_bots]
    #     await ctx.send(chatters_list[randint(0, len(chatters_list)) - 1])

    # @commands.cooldown(1, 10)
    # @commands.command(name="spin")
    # async def spin_the_wheel(self, ctx: commands.Context):
    #     username = ctx.author.name
    #     result = wheel.spin(username)
    #     for s in result:
    #         await sleep(1)
    #         await ctx.send(s)

    rare_spank_table = ["WooxSolo", "Odablock", "Framed", "J1mmy", "Faux", "Coxie", "Mmorpg", "Real_Matk", "SkillSpecs", "Mr_Mammal", "Alfie", "Roidie", "itswill", "SkiddlerRS", "Dino_xx", "JagexModAsh", "FBI_Survelliance_Van_381b"]

    @commands.cooldown(1, 10)
    @commands.command(name="spank")
    async def spank(self, ctx: commands.Context):
        if randint(0, 99) == 0:
            spanked = self.rare_spank_table[randint(0, len(self.rare_spank_table) - 1)]
        else:
            spanked = self.get_random_user(ctx)

        await ctx.send(f"{ctx.author.name} has spanked {spanked} peepoShy")

    @commands.cooldown(1, 10)
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

    @commands.command(name="coins")
    async def info_coins(self, ctx: commands.Context):
        await ctx.reply(f"Available coin commands: !add_coins <user> <amount>, !get_coins <user>, !gamble <amount>, !top_coins")

    @commands.command(name="add_coins")
    async def add_coins(self, ctx: commands.Context):
        if not self.check_if_mod(ctx.author):
            await ctx.reply(f"You're not a moderator x0r6ztGiggle")
            return

        args = ctx.message.content.split(" ")[1:]
        if len(args) < 2:
            await ctx.send(f"Usage: !add_coins <user or all> <amount>")
            return
        try:
            amount = int(args[1])
        except ValueError:
            await ctx.send(f"Invalid amount: {args[1]}")
            return
        except IndexError:
            amount = 1

        if args[0] == "all":
            chatters_list = [chatter.name for chatter in list(ctx.chatters) if chatter.name not in known_bots]
            self.db.add_coins(chatters_list, amount)
            await ctx.send(f"Gave everyone {amount} coins")
        else:
            self.db.add_coins([args[0]], amount)
            await ctx.send(f"Gave {args[0]} {amount} coins")

    @commands.command(name="get_coins")
    async def get_coins(self, ctx: commands.Context):
        args = ctx.message.content.split(" ")[1:]
        if len(args) > 0:
            user = args[0]
        else:
            user = ctx.author.name

        await ctx.send(f"{user} has {self.db.get_coins(user)} coins.")

    @commands.command(name="top_coins")
    async def gamble_coins(self, ctx: commands.Context):
        await ctx.send(f"soon (tm)")

    @commands.command(name="gamble")
    async def gamble_coins(self, ctx: commands.Context):
        try:
            desired_gambling_amount = ctx.message.content.split(" ")[1:][0]
        except IndexError:
            await ctx.send("No amount given, use !gamble <amount>")
            return
        current_amount = int(self.db.get_coins(ctx.author.name))
        if current_amount == 0:
            await ctx.send(f"{ctx.author.name} has no coins to gamble with!")

        if "all" == desired_gambling_amount:
            gambled_amount = current_amount
        elif "%" in desired_gambling_amount:
            try:
                gambled_amount = float(desired_gambling_amount[:-1]) / 100
            except ValueError:
                await ctx.send(f"Invalid amount: {desired_gambling_amount}")
                return
            gambled_amount = current_amount * gambled_amount
        else:
            desired_gambling_amount = desired_gambling_amount.lower()
            desired_gambling_amount = desired_gambling_amount.replace("k", "000")
            desired_gambling_amount = desired_gambling_amount.replace("m", "000000")
            try:
                gambled_amount = int(desired_gambling_amount)
            except ValueError:
                await ctx.send(f"Invalid amount: {desired_gambling_amount}")
                return
        if current_amount < gambled_amount:
                await ctx.send(f"You can not gamble {gambled_amount} coins, you only have {current_amount} coins")
                return
        elif gambled_amount < 0:
                await ctx.send(f"You can not gamble a negative amount of coins.")
                return

        current_amount = current_amount - gambled_amount
        gamble_outcome = randint(0, 100)
        if gamble_outcome < 50:
            await ctx.send(f"{ctx.author.name} rolled a {gamble_outcome} and lost {gambled_amount} coins.")
            new_amount = current_amount
        elif gamble_outcome == 69:
            await ctx.send(f"NICE BONUS!!! {ctx.author.name} rolled a {gamble_outcome} and got 4x their gamble back!.")
            new_amount = current_amount + gambled_amount * 4
        elif gamble_outcome == 73:
            await ctx.send(f"LaughHard NO WAY BONUS LaughHard !!! {ctx.author.name} rolled a {gamble_outcome} and got 4x their gamble back!.")
            new_amount = current_amount + gambled_amount * 4
        elif gamble_outcome == 100:
            await ctx.send(f"Pog BONUS Pog {ctx.author.name} rolled a {gamble_outcome} and got 4x their gamble back!.")
            new_amount = current_amount + gambled_amount * 4
        else:
            await ctx.send(f"{ctx.author.name} rolled a {gamble_outcome} and got 2x their gamble back!.")
            new_amount = current_amount + gambled_amount * 2
        await sleep(0.5)
        await ctx.send(f"{ctx.author.name} now has {new_amount} coins.")
        self.db.update_coins(ctx.author.name, new_amount)




    #------------------------------------
    # CHANNEL POINT REDEMPTIONS
    #------------------------------------

    @pubsub_client.event()
    async def event_pubsub_channel_points(event: pubsub.PubSubChannelPointsMessage):
        title = event.reward.title
        if title == "Add a seaman to the arc":
            new_amount = bot.db.insert_seaman(1)
            bot.send_message(f"Thank you for adding more seamen to the arc. The arc now has {new_amount} seamen peepoMayo")
            
        elif title == "Spin The arcWheel":
            username = event.user.name
            result = wheel.spin(username)
            for s in result:
                await sleep(1)
                bot.send_message(s)

if __name__ == "__main__":
    bot = ArcBot()
    bot.run()
