from twitchio.ext import commands

class Sailing(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ship")
    async def ship_stats(self, ctx: commands.Context):
        pass

    @commands.command(name="scout")
    async def ship_scout(self, ctx: commands.Context):
        pass

    @commands.command(name="upgrade")
    async def ship_upgrade(self, ctx: commands.Context):
        pass

    @commands.command(name="sail")
    async def ship_sail(self, ctx: commands.Context):
        pass

    @commands.command(name="board")
    async def ship_board(self, ctx: commands.Context):
        pass

    @commands.command(name="bombard")
    async def ship_bombard(self, ctx: commands.Context):
        pass

    @commands.command(name="port")
    async def ship_port(self, ctx: commands.Context):
        pass