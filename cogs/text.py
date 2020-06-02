import discord
from discord.ext import commands
import aiohttp
import random
from art import *
import libmorse as morse

class Text(commands.Cog):
	"""Some cool text features."""
	def __init__(self, client):
		self.client = client
	
	
	@commands.command()
	async def morsify(self, ctx, *,word:str):
		"""Generate morse code from a text"""
				
		msg = morse.morsify(word)
		
		if len(list(word)) > 500:
			await ctx.send("This string is too big for me to decode!")
		else:
			try:
				await ctx.send(msg)
			except:
				await ctx.send("Something went wrong!")
	
	@commands.command()
	async def demorse(self, ctx, *,word:str):
		"""Read morse code"""
		
		msg = morse.demorse(word)
			
		if len(list(word)) > 2000:
			await ctx.send("This string is too big for me to decode!")
		else:
			try:
				await ctx.send(msg)
			except:
				await ctx.send("Something went wrong!")
	
	@commands.command(name="text2art", aliases=["textart"])
	async def t2a(self, ctx, *, text:str):
		"""Generate random art from text."""
		art = text2art(text, "rand")
		if len(art) <0:
			await ctx.send("Cant art that!")
		else:
			try:
				await ctx.send("```" + art + "```")
			except Exception as e:
				await ctx.send(e)
	
	@commands.command(name="randart", aliases=["randomart"])
	async def _randart(self, ctx):
		"""Generate random art."""
		art = randart()
		await ctx.send("```" + art + "```")
	
	@commands.command(aliases=["wiz", "magic"])
	async def wizard(self, ctx, *, text:str):
		"""Generate random art from text Wizard Format"""
		art = text2art(text, "wizard")
		if len(art) <0:
			await ctx.send("Cant art that!")
		else:
			try:
				await ctx.send("```" + art + "```")
			except Exception as e:
				await ctx.send(e)
	
	@commands.command(aliases=["randstyle", "rns"])
	async def randomstyle(self, ctx, *, text:str):
		"""Some cool font style."""
		art = text2art(text, "random-na")
		if len(art) <0:
			await ctx.send("Cant art that!")
		else:
			try:
				await ctx.send(art)
			except Exception as e:
				await ctx.send(e)
	
	@commands.command(aliases=["usd"])
	async def upsidedown(self, ctx, *, text:str):
		"""Upsidedown text."""
		art = text2art(text, "upsidedown")
		if len(art) <0:
			await ctx.send("Cant art that!")
		else:
			try:
				await ctx.send(art)
			except Exception as e:
				await ctx.send(e)
	
	@commands.command(aliases=["h4ck3r", "hkr", "leet"])
	async def h4k3r(self, ctx, *, text:str):
		"""h4ck3r"""
		art = text2art(text, "h4k3r")
		if len(art) <0:
			await ctx.send("Cant art that!")
		else:
			try:
				await ctx.send(art)
			except Exception as e:
				await ctx.send(e)
	
	@commands.command(aliases=["bs"])
	async def blacksquare(self, ctx, *, text:str):
		"""Black Square"""
		art = text2art(text, "black-square")
		if len(art) <0:
			await ctx.send("Cant art that!")
		else:
			try:
				await ctx.send(art)
			except Exception as e:
				await ctx.send(e)
				
	@commands.command(aliases=["ws"])
	async def whitesquare(self, ctx, *, text:str):
		"""White Square"""
		art = text2art(text, "white-square")
		if len(art) <0:
			await ctx.send("Cant art that!")
		else:
			try:
				await ctx.send(art)
			except Exception as e:
				await ctx.send(e)
	
	@commands.command(aliases=["bb"])
	async def blackbubble(self, ctx, *, text:str):
		"""Black Square"""
		art = text2art(text, "black-bubble")
		if len(art) <0:
			await ctx.send("Cant art that!")
		else:
			try:
				await ctx.send(art)
			except Exception as e:
				await ctx.send(e)
	
	@commands.command()
	async def dab(self, ctx, *, text:str):
		"""Dab Dab Dab"""
		art = text2art(text, "dab")
		if len(art) <0:
			await ctx.send("Cant art that!")
		else:
			try:
				await ctx.send("```" + art + "```")
			except Exception as e:
				await ctx.send(e)
	
	
	
def setup(client):
	client.add_cog(Text(client))