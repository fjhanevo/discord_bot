import os
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


# --- Bot Setup --- 
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class StartBot(commands.Bot):
    """ Subclass inheriting from commands.Bot to customise startup functionality. """

    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        cogs_dir = "cogs"

        for filename in os.listdir(cogs_dir):
            if filename.endswith(".py"):
                await self.load_extension(f"{cogs_dir}.{filename[:-3]}")
                print(f"Successfully loaded cog: {filename}")

    async def on_ready(self):
        print("Bot loaded")


async def main():
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    level = logging.DEBUG

    discord.utils.setup_logging(handler=handler, level=level)

    bot = StartBot()
    await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
