import os
import discord
from discord.ext import commands


class DocBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        

        super().__init__(
            command_prefix = '!lol ',
            help_command=None,
            intents = intents
        )

    async def on_ready(self):
        print(f"{self.user.display_name} est connecté au serveur.")

        game = discord.Game("!lol commands to get info.")
        await self.change_presence(status = discord.Status.dnd, activity = game)
        async for guild in self.fetch_guilds(limit=1000):
            print(guild)

        print(self.intents.members)
    
    """ async def help(ctx):
        embed = discord.Embed(title=f'Bot Willump', color=0x50b9b3)
        embed.add_field(name="**Invite:**", value='If you want the bot on your server! You can get it [**here**](https://discord.com/api/oauth2/authorize?client_id=972468249218416711&permissions=8&scope=bot)!', inline= True)
        embed.add_field(name="**Commands:**", value="You can check **all available commands**, on the site http://127.0.0.1:5500/lolRank/site/index.html#commands\n or `!lol commands`")
        await ctx.send(embed = embed) """