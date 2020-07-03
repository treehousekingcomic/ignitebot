import discord
import json
import time
import os
from discord.ext import commands, tasks
import re
from itertools import groupby
from discord.utils import get
import dotenv
from datetime import datetime
import asyncpg

env_path = os.path.join(os.getcwd(), '.env')
dotenv.load_dotenv(dotenv_path=env_path)
#from Webserver import keep_alive

TOKEN = os.getenv("TOKEN")
DEVID = 579298652938305551


os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"


async def create_db_pool():
	bot.pgdb = await asyncpg.create_pool(host="localhost", database="main", user="shah", password="shah")

bot = commands.Bot(
    command_prefix="m!",
    description='Ignite Music',
    owner_id=DEVID,
    case_insensitive=True
)
bot.launch_time = datetime.utcnow()


@bot.event
async def on_ready():
	print(f'{bot.user} has connected to Discord! ID:{bot.user.id}')
        await bot.change_presence(activity=discord.Game(name="Trying to join 75+ servers😩"),
                                  status=discord.Status.online)
        for cog in cogs:
            bot.load_extension(cog)
        bot.load_extension("pro.delete_expired")
        bot.load_extension("pro.system")
        print("Total Users: " + str(len(bot.users)))
        print("Total Servers: " + str(len(bot.guilds)))
        bot.DEVUSER = bot.get_user(579298652938305551)
        DEVUSER = bot.DEVUSER
        shared = len(
            [g for g in bot.guilds
             if DEVUSER in g.members]
        )
        print("Total # of Shared Servers with DEV: " + str(shared))

@bot.event
async def on_message(message):
  await bot.process_commands(message)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

for filename in os.listdir('./admin'):
    if filename.endswith('.py') and filename.startswith("keychecker") == False:
        client.load_extension(f'admin.{filename[:-3]}')

client.loop.run_until_complete(create_db_pool())
client.load_extension('jishaku')


client.run(TOKEN)
