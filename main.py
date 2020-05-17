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

async def create_db_pool():
	client.pgdb = await asyncpg.create_pool(host="localhost", database="main", user="shah", password="shah")
	
	await client.pgdb.execute("""
	CREATE TABLE IF NOT EXISTS guilddata(
	id serial PRIMARY KEY,
	guildid bigint NOT NULL,
	prefix VARCHAR(20) NOT NULL,
	wnr bigint NULL,
	wci bigint NULL,
	bci bigint NULL,
	wr bigint NULL,
	igr bigint NULL,
	wlcmsg TEXT NULL,
	nameprefix TEXT NULL
	)
	""")
	
	await client.pgdb.execute("""
	CREATE TABLE IF NOT EXISTS admin(
	id serial PRIMARY KEY,
	name VARCHAR(50) NOT NULL,
	password VARCHAR(50) NOT NULL,
	userid bigint NOT NULL,
	loggedin INTEGER NOT NULL
	)
	""")	
	await client.pgdb.execute("""
	CREATE TABLE IF NOT EXISTS keys(
	key VARCHAR(50) NOT NULL,
	guildid bigint NULL,
	created DATE NOT NULL DEFAULT CURRENT_DATE,
	expire DATE NOT NULL
	)
	""")
	await client.pgdb.execute("""
	CREATE TABLE IF NOT EXISTS rr(
	id serial PRIMARY KEY,
	messageid bigint NOT NULL,
	roleid bigint NOT NULL,
	emojiid bigint NOT NULL,
	guildid bigint NOT NULL
	)
	""")
	
	await client.pgdb.execute("""
	CREATE TABLE IF NOT EXISTS todos(
	id serial PRIMARY KEY,
	userid bigint NOT NULL,
	content TEXT NOT NULL
	)
	""")
	
	await client.pgdb.execute("""
	CREATE TABLE IF NOT EXISTS levels(
	id serial PRIMARY KEY,
	userid bigint NOT NULL,
	guildid bigint NOT NULL,
	exp bigint NOT NULL,
	level bigint NOT NULL,
	prev_msg TEXT NULL
	)""")
	
	await client.pgdb.execute("""
	CREATE TABLE IF NOT EXISTS tags(
	id serial PRIMARY KEY,
	tagname VARCHAR(200) NOT NULL,
	content TEXT NULL,
	userid bigint NOT NULL,
	guildid bigint NOT NULL,
	tagtype VARCHAR(10) NULL,
	ttp VARCHAR(20) NOT NULL,
	emt VARCHAR(200) NULL,
	emb TEXT NULL,
	rid bigint NULL
	)""")
	
	await client.pgdb.execute("""
	CREATE TABLE IF NOT EXISTS cash(
	id serial PRIMARY KEY,
	userid bigint NOT NULL,
	cash bigint NOT NULL)"""
	)
	
	await client.pgdb.execute("""
	CREATE TABLE IF NOT EXISTS cmduse(
	id serial PRIMARY KEY,
	name VARCHAR(50) NOT NULL,
	uses bigint NOT NULL DEFAULT 1
	)
	""")
	
	await client.pgdb.execute("""
	CREATE TABLE IF NOT EXISTS convo(
	id serial PRIMARY KEY,
	userid bigint NOT NULL,
	channelid bigint NOT NULL
	)
	""")
	
	
	

async def get_prefix(client, message):
  id = message.guild.id
  res = await client.pgdb.fetchrow("SELECT prefix FROM guilddata WHERE guildid = $1" , id)
  prefix = res['prefix']
  return prefix

client = commands.AutoShardedBot(command_prefix=get_prefix)
client.launch_time = datetime.utcnow()
client.remove_command('help')

async def is_prem(self,gld):
		data = await client.pgdb.fetchrow(f"SELECT * FROM keys WHERE guildid = $1", gld)
		if data:
			return Tru
		else:
			return False
			
async def tag_is_prem(tagname, gld):
		data = await client.pgdb.fetchrow(f"SELECT * FROM tags WHERE tagname = $1 AND guildid = $2", tagname, gld)
		tagtype = data['tagtype']
		
		if tagtype == 'free':
			return False
		else:
			return True
  
	
#predata = db.execute("SELECT prefix FROM guilddata"

@client.event
async def on_ready():
	print("Bot is ready")
	client.load_extension("admin.keychecker")

@client.event
async def on_message(message):
  await client.process_commands(message)
  

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
for filename in os.listdir('./games'):
  if filename.endswith('.py'):
    client.load_extension(f"games.{filename[:-3]}")

for filename in os.listdir('./admin'):
    if filename.endswith('.py') and filename.startswith("keychecker") == False:
        client.load_extension(f'admin.{filename[:-3]}')

client.loop.run_until_complete(create_db_pool())
client.load_extension('jishaku')
#client.load_extension('cogs.tags')
#client.load_extension('cogs.todo')
client.run(TOKEN)
#client.load_extension('admin.keychecker')
#print("Hi")
#Added a new comment