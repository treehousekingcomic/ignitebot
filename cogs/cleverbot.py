import discord
from discord.ext import commands
import re
import asyncpg
import async_cleverbot as cl
import dotenv
import os

env_path = os.path.join(os.getcwd(), '.env')
dotenv.load_dotenv(dotenv_path=env_path)

CBKEY=os.getenv("CBKEY")


class CleverBot(commands.Cog, name="Cleverbot"):
	"""Ask cleverbot question. Or start conversation."""
	
	def __init__(self, client):
		self.client = client
		self.cb = cl.Cleverbot(CBKEY)
	
	async def get_prefix(self, id):
		data = await self.client.pgdb.fetchrow("SELECT * FROM guilddata WHERE guildid = $1", id)
		return data['prefix']	
	
	async def ucmd(self, cmd:str):
		data = await self.client.pgdb.fetchrow("SELECT * FROM cmduse WHERE name = $1", cmd)
  	
		if data:
			uses = data['uses'] + 1
			await self.client.pgdb.execute("UPDATE cmduse SET uses = $1 WHERE name = $2", uses, data['name'])
		else:
			await self.client.pgdb.execute("INSERT INTO cmduse(name, uses) VALUES($1, $2)", cmd, 1)
	
	@commands.command()
	@commands.cooldown(1, 7, commands.BucketType.user)
	async def ask(self, ctx, *, question:str):
		"""Ask a question to bot."""
		await self.ucmd("ask")
		async with ctx.channel.typing():
			resp = await self.cb.ask(question)
			await ctx.send(f"> {question} \n{ctx.author.mention} {resp.text}")
	
	@ask.error
	async def on_error(self, ctx, error):
		if isinstance(error, commands.CommandOnCooldown):
			pass
			#await ctx.send("On cooldown")
	
	@commands.command(aliases=['conv', 'talk'])
	async def conversation(self, ctx):
		"""Start conversation with bot."""
		await self.ucmd("convo")
		prefix = await self.get_prefix(ctx.guild.id)
		
		data = await self.client.pgdb.fetchrow("SELECT * FROM convo WHERE userid = $1", ctx.author.id)
		if not data:
			await self.client.pgdb.execute("INSERT INTO convo(userid, channelid) VALUES($1, $2)", ctx.author.id, ctx.channel.id)
			await ctx.send(f"Starting conversation with {ctx.author.mention}. Say something or ask something. I will try to answer. Type `stop` anytime to stop conversation.")
			def check(m):
				return m.author == ctx.author and m.channel == ctx.channel
		
			while True:
				try:
					msg = await self.client.wait_for("message", timeout=30, check=check)
					if msg.content.lower() == "stop":
						await ctx.send("Ok!")
						await self.client.pgdb.execute("DELETE FROM convo WHERE userid =$1", ctx.author.id)
						break
					else:
						if msg.content.lower().startswith(prefix):
							pass
						else:
							async with ctx.channel.typing():
								resp = await self.cb.ask(msg.content)
								await ctx.send(f"> {msg.content} \n{ctx.author.mention} {resp.text}")
				except:
					await ctx.send("You are late!")
					await self.client.pgdb.execute("DELETE FROM convo WHERE userid =$1", ctx.author.id)
					break
		else:
			if data['channelid'] == ctx.channel.id:
				inn = "this channel"
			else:
				chan = discord.utils.get(ctx.guild.channels, id=data['channelid'])
				if chan is not None:
					inn = chan.mention
				else:
					inn = "the channel where you started conversation"
				
			await ctx.send(f"You already in a conversation! Type stop in {inn} to stop that.")
	
def setup(client):
  client.add_cog(CleverBot(client))