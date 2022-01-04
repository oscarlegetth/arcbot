import os
from asyncio.tasks import sleep, wait
import random
from time import time
from dotenv import load_dotenv
from random import randint
import pkg_resources

from osrsbox import items_api
import twitchio
from twitchio import message
from twitchio.errors import AuthenticationError
from twitchio.ext import commands, pubsub, routines
from twitchio.ext.commands.core import Context, command, cooldown
from twitchio.message import Message
import asyncio
from twitchio.models import AutomodCheckMessage

from twitchio.user import UserBan
from ArcBot.sailing import Sailing
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
chatters_cache = ["dfaddf"]
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
        bot.add_cog(Sailing(bot))

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
        self.add_coins_routine.start()

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
        
        global chatters_cache
        chatters_cache = (await bot.get_context(ctx)).chatters

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
        args[1] = args[1].lower()
        args[1] = args[1].replace("k", "000")
        args[1] = args[1].replace("m", "000000")
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
            username = args[0].lower()
            self.db.add_coins([username], amount)
            await ctx.send(f"Gave {username} {amount} coins")

    @routines.routine(minutes=5, wait_first=True)
    async def add_coins_routine(self):
        chatters_list = [chatter.name for chatter in list(chatters_cache) if chatter.name not in known_bots]
        self.db.add_coins(chatters_list, 100)

    @commands.command(name="get_coins")
    async def get_coins(self, ctx: commands.Context):
        args = ctx.message.content.split(" ")[1:]
        if len(args) > 0:
            user = args[0].lower()
        else:
            user = ctx.author.name

        await ctx.send(f"{user} has {self.db.get_coins(user)} coins.")

    @commands.command(name="top_coins")
    async def top_coins(self, ctx: commands.Context):
        top_coin_owners = self.db.get_top_coins()
        top_coin_owners_string = ", ".join([str(row["username"] + ": " + str(row["val"])) for row in top_coin_owners])
        await ctx.send(f"Top coin owners: {top_coin_owners_string}")

    @commands.cooldown(rate=1, per=5)
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
            return

        if "all" == desired_gambling_amount:
            gambled_amount = current_amount
        elif "%" in desired_gambling_amount:
            try:
                gambled_amount = float(desired_gambling_amount[:-1]) / 100
            except ValueError:
                await ctx.send(f"Invalid percentage amount: {desired_gambling_amount}")
                return
            gambled_amount = int(current_amount * gambled_amount)
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
            gamble_result_message = f"{ctx.author.name} rolled a {gamble_outcome} and lost {gambled_amount} coins."
            new_amount = current_amount
        elif gamble_outcome == 69:
            gamble_result_message = f"NICE BONUS!!! {ctx.author.name} rolled a {gamble_outcome} and got 4x their gamble back!."
            new_amount = current_amount + gambled_amount * 4
        elif gamble_outcome == 73:
            gamble_result_message = f"LaughHard NO WAY BONUS LaughHard !!! {ctx.author.name} rolled a {gamble_outcome} and got 4x their gamble back!."
            new_amount = current_amount + gambled_amount * 4
        elif gamble_outcome == 100:
            gamble_result_message = f"Pog BONUS Pog {ctx.author.name} rolled a {gamble_outcome} and got 4x their gamble back!."
            new_amount = current_amount + gambled_amount * 4
        else:
            gamble_result_message = f"{ctx.author.name} rolled a {gamble_outcome} and got 2x their gamble back!."
            new_amount = current_amount + gambled_amount * 2
        await sleep(0.5)
        await ctx.send(f"{gamble_result_message} {ctx.author.name} now has {new_amount} coins.")
        self.db.update_coins(ctx.author.name, new_amount)

    @commands.command(name="bet")
    async def info_bet(self, ctx: commands.Context):
        await ctx.reply("Type \"!place_bet <total_level>\" to guess at which total level arcReign's HCIM will die. Type \"!check_bet\" to check your bet.")


    async def place_bet(self, username, bet, ctx):
        try:
            bet = int(bet)
        except ValueError:
            await ctx.reply(f"{bet} is not an integer.")
            return
        if bet < 32 or bet > 2277:
            await ctx.reply(f"{bet} is not a valid total level.")
            return
        self.db.insert_hcim_bet(username, bet)
        await ctx.reply(f"{username} has placed a bet! {bet}.")

    @commands.command(name="place_bet")
    async def place_hcim_bet(self, ctx: commands.Context):
        username = ctx.author.name
        current_bet = self.db.get_hcim_bet(username)
        if current_bet:
            await ctx.reply(f"{username} already has a bet: {current_bet} ask moderator if you would like your bet changed.")
            return
        args = ctx.message.content.split(" ")[1:]
        if len(args) == 0:
            await ctx.reply("Type \"!place_bet <total_level>\" to guess at which total level arcReign's HCIM will die.")
            return
        bet = args[0]
        await self.place_bet(username, bet, ctx)

    @commands.command(name="mod_place_bet")
    async def mod_place_hcim_bet(self, ctx: commands.Context):
        if not self.check_if_mod(ctx.author):
            await ctx.reply(f"You're not a moderator x0r6ztGiggle")
            return

        args = ctx.message.content.split(" ")[1:]
        if len(args) < 2:
            await ctx.reply("Type \"!mod_place_bet <username> <total_level>\" to set a user's guess at which total level arcReign's HCIM will die.")
            return
        username = args[0].lower()
        bet = args[1]
        await self.place_bet(username, bet, ctx)

    @commands.command(name="check_bet")
    async def check_hcim_bet(self, ctx: commands.Context):
        username = ctx.author.name
        bet = self.db.get_hcim_bet(username)
        if not bet:
            await ctx.reply(f"{username}'s has not placed a bet yet. Place a bet with \"!place_bet <total_level>\".")
        else:
            await ctx.reply(f"{username}'s bet is {bet}.")

    @commands.command(name="sailing")
    async def sailing(self, ctx: commands.Context):
        if self.check_if_mod(ctx.author):
            args = ctx.message.content.split(" ")[1:]
            if len(args) > 1:
                if args[0] == "enable" and "Sailing" not in bot.cogs:
                    bot.add_cog(Sailing(bot))
                elif args[1] == "disable" and "Sailing" in bot.cogs:
                    bot.remove_cog("Sailing")

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

        elif title == "Buy ship and crew":
            pass

if __name__ == "__main__":
    bot = ArcBot()
    bot.run()
