import discord
from discord.ext import commands
import re
import asyncpg

class Emoji(commands.Cog):
	"""Emoji tools."""
	def __init__(self, client):
		self.client = client
	
	async def ucmd(self, cmd:str):
		data = await self.client.pgdb.fetchrow("SELECT * FROM cmduse WHERE name = $1", cmd)
		
		if data:
			uses = data['uses'] + 1
			await self.client.pgdb.execute("UPDATE cmduse SET uses = $1 WHERE name = $2", uses, data['name'])
		else:
			await self.client.pgdb.execute("INSERT INTO cmduse(name, uses) VALUES($1, $2)", cmd, 1)
  
	@commands.command()
	async def emojis(self, ctx):
		"""See all the emojis this server have"""
		msg = ""
		for emoji in ctx.guild.emojis:
			msg += str(emoji) + " "
		
		await ctx.send(msg)
    
	@commands.command()
	async def snipe(self, ctx, msgid:int):
		"""Get links of emoji from a message by putting its message id."""
		await self.ucmd("snipe")
		
		try:
			msg = await ctx.channel.fetch_message(msgid)
		except:
			await ctx.send("No msg found with this id!")
		
		if msg is not None:
			emojis = re.findall("<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>", msg.content)
		if len(emojis) == 0:
			await ctx.send("No server emoji found!")
		else:
			msg = ""
		for e in emojis:
			try:
				emj = discord.utils.get(ctx.guild.emojis, id=int(e[2]))
				msg += f"**{e[1]}** {str(emj)} \n<{emj.url}>\n"
			except:
				pass
		if len(msg) !=0:
			await ctx.send(msg)
		else:
			await ctx.send("These emojis are not in this server!")

def setup(client):
  client.add_cog(Emoji(client))