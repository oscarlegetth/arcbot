from random import randint
from twitchio.ext import commands, routines
from asyncio import sleep

class Gamble(commands.Cog):

    def __init__(self, bot: commands.Bot):
        super()
        self.bot = bot
        self.add_coins_routine.start()
    
    @commands.command(name="coins")
    async def coins(self, ctx: commands.Context):
        await ctx.reply(f"Available coin commands: !add_coins <user> <amount>, !get_coins <user>, !gamble <amount>, !top_coins")

    @commands.command(name="add_coins")
    async def add_coins(self, ctx: commands.Context):
        if not self.bot.check_if_mod(ctx.author):
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
            chatters_list = [chatter.name for chatter in list(ctx.chatters) if chatter.name not in self.bot.known_bots]
            self.bot.db.add_coins(chatters_list, amount)
            await ctx.send(f"Gave everyone {amount} coins")
        else:
            username = args[0].lower()
            self.bot.db.add_coins([username], amount)
            await ctx.send(f"Gave {username} {amount} coins")

    @routines.routine(minutes=5, wait_first=True)
    async def add_coins_routine(self):
        chatters_list = [chatter.name for chatter in list(self.bot.chatters_cache) if chatter.name not in self.bot.known_bots]
        self.bot.db.add_coins(chatters_list, 100)

    @commands.command(name="get_coins")
    async def get_coins(self, ctx: commands.Context):
        args = ctx.message.content.split(" ")[1:]
        if len(args) > 0:
            user = args[0].lower()
        else:
            user = ctx.author.name

        await ctx.send(f"{user} has {self.bot.db.get_coins(user)} coins.")

    @commands.command(name="top_coins")
    async def top_coins(self, ctx: commands.Context):
        top_coin_owners = self.bot.db.get_top_coins()
        top_coin_owners_string = ", ".join([str(row["username"] + ": " + str(row["val"])) for row in top_coin_owners])
        await ctx.send(f"Top coin owners: {top_coin_owners_string}")

    @commands.cooldown(1, 5, commands.cooldowns.Bucket.user)
    @commands.command(name="gamble")
    async def gamble(self, ctx: commands.Context):
        try:
            desired_gambling_amount = ctx.message.content.split(" ")[1:][0]
        except IndexError:
            await ctx.send("No amount given, use !gamble <amount>")
            return
        current_amount = int(self.bot.db.get_coins(ctx.author.name))
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
        elif gambled_amount <= 0:
                await ctx.send(f"You can not gamble less than 1 coin.")
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
        self.bot.db.update_coins(ctx.author.name, new_amount)
