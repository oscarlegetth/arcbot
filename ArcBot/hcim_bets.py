from twitchio.ext import commands

class HCIM_bets(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="bet")
    async def bet(self, ctx: commands.Context):
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
        self.bot.db.insert_hcim_bet(username, bet)
        await ctx.reply(f"{username} has placed a bet! {bet}.")

    @commands.command(name="place_bet")
    async def place_bet(self, ctx: commands.Context):
        username = ctx.author.name
        current_bet = self.bot.db.get_hcim_bet(username)
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
    async def mod_place_bet(self, ctx: commands.Context):
        if not self.bot.check_if_mod(ctx.author):
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
    async def check_bet(self, ctx: commands.Context):
        args = ctx.message.content.split(" ")[1:]
        if len(args) > 0:
            username = args[0]
        else:
            username = ctx.author.name
        bet = self.bot.db.get_hcim_bet(username)
        if not bet:
            await ctx.reply(f"{username}'s has not placed a bet yet. Place a bet with \"!place_bet <total_level>\".")
        else:
            await ctx.reply(f"{username}'s bet is {bet}.")
