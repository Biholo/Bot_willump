from asyncio import tasks
import discord
import random

class Setting(discord.ext.commands.Cog, name="Setting module"):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds = 5)
    async def status(self):
        game_activity = discord.Game("!lol commands for info")
        await self.bot.change_presence(status = discord.Status.dnd, activity = game_activity)

