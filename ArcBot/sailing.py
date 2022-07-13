from random import random
from time import time
from twitchio.ext import commands

from ArcBot.ship import Ship

class Sailing(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = None
        self.current_ships_sailing : dict[str, Ship] = {}

    #------------------------------------
    # COMMANDS
    #------------------------------------

    @commands.command(name="ship")
    async def ship_stats(self, ctx: commands.Context):
        ship = Ship.get_ship(self.db, ctx.author.name)
        if not ship:
            await ctx.reply(f"You have not yet bought a ship! Buy a ship with !buyship")
        elif ship in self.current_ships_sailing:
            await ctx.reply(f"Your ship is currents ailing on the seven seas! It will be back in {int(600 - (time() - ship.stats.time_set_sail))} seconds")
        else:
            await ctx.reply(f"Your ship is at port, ready to set sail! {ship.get_stats_str()}")
        
    @commands.command(name="buyship")
    async def buy_ship(self, ctx: commands.Context):
        ship = Ship(ctx.author.name)
        ship.save_ship(self.db)
        await ctx.reply(f"You have bought a new ship! {ship.get_stats_str()}")

    @commands.command(name="scout")
    async def ship_scout(self, ctx: commands.Context):
        await ctx.reply(f"You scout the seas and see " + ', '.join(self.current_ships_sailing.keys()))


    @commands.command(name="upgrade")
    async def ship_upgrade(self, ctx: commands.Context):
        pass

    @commands.command(name="setsail")
    async def ship_sail(self, ctx: commands.Context):
        username = ctx.author.name
        if username in self.current_ships_sailing:
            ship = self.current_ships_sailing[username]
            await ctx.reply(f"Your ship is already sailing on the seven seas! It will be back in {int(600 - (time() - ship.stats.time_set_sail))} seconds")
        else:
            ship = Ship.get_ship(self.db, username)
            ship.set_sail()
            self.current_ships_sailing[username] = ship
            await ctx.reply(f"Your ship has set sail! It will be back in 10 minutes.")
            

    @commands.command(name="board")
    async def ship_board(self, ctx: commands.Context):
        pass

    @commands.command(name="bombard")
    async def ship_bombard(self, ctx: commands.Context):
        pass

    @commands.command(name="port")
    async def ship_port(self, ctx: commands.Context):
        pass


    #------------------------------------
    # HELPER FUNCTIONS
    #------------------------------------

    async def update(self):
        current_time = time()
        for username, ship in self.current_ships_sailing.items():
            if current_time - ship.stats.time_set_sail >= 600:
                del(self.current_ships_sailing[username])
                ship.stats.time_set_sail = -1
                loot = (ship.stats.cannons + ship.stats.sails + ship.stats.crew_current_amount) * ship.stats.hp * (random() / 3 + 2 / 3)
                await self.bot.send_message(f"@{username} Your ship has returned! It plundered a total of {loot} loot!")
