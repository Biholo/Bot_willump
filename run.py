import discord
import os
from dotenv import load_dotenv
from package.clients.bot_client import DocBot
from package.cogs.commandes import Commandes


load_dotenv(dotenv_path="config")



bot = DocBot()

bot.add_cog(Commandes(bot))
bot.run(os.getenv("TOKEN"))
