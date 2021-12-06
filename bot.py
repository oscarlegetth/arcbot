import os
from asyncio.tasks import sleep
from dotenv import load_dotenv
from random import randint

from osrsbox import items_api
from twitchio import chatter
from twitchio.ext import commands
from twitchio.message import Message
import asyncio

import wheel


# pip packages: twitchio, osrsbox, websocket, asyncio, dotenv
# mostly code from
# https://dev.to/ninjabunny9000/let-s-make-a-twitch-bot-with-python-2nd8

# global objects

load_dotenv()
items = items_api.load()
wheel = wheel.Wheel()
known_bots = ["arcbot73", "creatisbot", "nightbot", "anotherttvviewer", "streamlabs"]

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

    async def event_ready(self):
        """Called once when the bot goes online."""
        message = f"{os.environ['BOT_NICK']} is online!"
        await asyncio.sleep(1)
        print(message)
        self.send_message(message)
        
    def send_message(self, message):
        chan = bot.get_channel("arcreign")
        loop = asyncio.get_event_loop()
        loop.create_task(chan.send(message))
    
    def remove_7tv_chars(self, message):
        weird_7tv_chars = " 󠀀 󠀀" # weird characters added at the end of messages by 7tv, not just spaces!
        return  message.strip(weird_7tv_chars)

    def get_random_user(self, ctx):
        chatters_list = [chatter.name for chatter in list(ctx.chatters) if chatter.name not in known_bots]
        return chatters_list[randint(0, len(chatters_list)) - 1]

    async def event_message(self, ctx):
        """Runs every time a message is sent in chat."""

        # make sure the bot ignores itself
        if type(ctx) is Message:
            if not ctx.author:
                return
            if ctx.author and ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
                return
            message = self.remove_7tv_chars(ctx.content)
            # respond to messages ending with "er?"
            if message[-3:] == "er?" and randint(0, 9) == 0:
                self.send_message(f"{message.split()[-1]} I hardly know her!!! LaughHard")
        else:
            print(f"Unexpected context encountered. Type: {type(ctx)} str: {str(ctx)}")
        ctx.content = self.remove_7tv_chars(ctx.content)
        await self.handle_commands(ctx)

    @commands.command(name='test')
    async def test(self, ctx: commands.Context):
        """Adds a '!test' command to the bot."""
        await ctx.send('test passed!')

    @commands.command(name="task")
    async def task(self, ctx: commands.Context):
        if not "moderator" in ctx.author.badges:
            return
        first_space_index = ctx.message.content.find(" ")
        if first_space_index == -1:
            return
        message = ctx.message.content[first_space_index + 1:]
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

    @commands.cooldown(1, 10)
    @commands.command(name="spin")
    async def spin_the_wheel(self, ctx: commands.Context):
        username = ctx.author.name
        result = wheel.spin(username)
        for s in result:
            await sleep(1)
            await ctx.send(s)

    @commands.cooldown(1, 10)
    @commands.command(name="spank")
    async def spank(self, ctx: commands.Context):
        spanked = self.get_random_user(ctx)
        await ctx.send(f"{ctx.author.name} has spanked {spanked} peepoShy")


if __name__ == "__main__":
    bot = ArcBot()
    bot.run()
