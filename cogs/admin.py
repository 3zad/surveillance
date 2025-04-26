import nextcord
from nextcord.ext import commands
import sys
from db.MainDatabase import MainDatabase

class AdminCommands(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.db = MainDatabase()
        
        self.config = config
        self.admins = config["owners"]

    @nextcord.slash_command(name="shutdown", description="(Admin command) Turn off the bot")
    async def shutdown(self, ctx):
        if ctx.user.id in self.admins:
            await ctx.send("Shutting down!")
            sys.exit(0)

    @nextcord.slash_command(name="a", description="a")
    async def a(self, ctx, f1, f2):
        if ctx.user.id not in self.admins:
            return
        channel = self.bot.get_channel(int(f1))
        await channel.send(f2)