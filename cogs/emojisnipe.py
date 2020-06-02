import discord
from discord.ext import commands
import re
import asyncpg

class Emoji(commands.Cog):
	"""Emoji tools."""
	def __init__(self, client):
		self.client = client
	
	@commands.command()
	async def allemoji(self, ctx):
		"""See all the emojis this server have"""
		msg = ""
		for emoji in ctx.guild.emojis:
			msg += str(emoji) + " "
		
		await ctx.send(msg)
    
	@commands.command()
	async def emojilinks(self, ctx, emojis:commands.Greedy[discord.Emoji]):
		"""Get links of emoji from a message by putting its message id."""
		emojis = set(emojis)
		
		if len(emojis) ==0:
			return await ctx.send("No emoji supplied.")
		msg = ""
		for emoji in emojis:
			msg += f"**{emoji.name}** {str(emoji)} <{emoji.url}> \n\n"
		
		await ctx.send(msg)
		
def setup(client):
  client.add_cog(Emoji(client))