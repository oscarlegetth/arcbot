import os
from random import randint

from osrsbox import items_api
from twitchio.ext import commands

# pip packages: twitchio, osrsbox
# mostly code from
# https://dev.to/ninjabunny9000/let-s-make-a-twitch-bot-with-python-2nd8

# global objects

bot = commands.Bot(
    # set up the bot
    irc_token=os.environ['TMI_TOKEN'],
    client_id=os.environ['CLIENT_ID'],
    nick=os.environ['BOT_NICK'],
    prefix=os.environ['BOT_PREFIX'],
    initial_channels=[os.environ['CHANNEL']]
)

items = items_api.load()

# helper methods

def get_random_item():
    return items[randint(0, len(items))].name

def get_random_items(i):
    return list(set([get_random_item() for _ in range(i)]))


@bot.event
async def event_ready():
    """Called once when the bot goes online."""
    print(f"{os.environ['BOT_NICK']} is online!")
    ws = bot._ws  # this is only needed to send messages within event_ready
    await ws.send_privmsg(os.environ['CHANNEL'], f"/me has landed!")


@bot.command(name='test')
async def test(ctx):
    """Adds a '!test' command to the bot."""
    await ctx.send('test passed!')

@bot.event
async def event_message(ctx):
    """Runs every time a message is sent in chat."""

    # make sure the bot ignores itself and the streamer
    if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
        return

    # attempt at repsonding to messages that end in 'er?'
    if ctx.message[-3, -1] == "er?" and randint(0, 10) == 0 :
        await ctx.send("I hardly know her!!! LaughHard")


    await ctx.send()

if __name__ == "__main__":
    bot.run()

# do not add anything below this line, it won't run
