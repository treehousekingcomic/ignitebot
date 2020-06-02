import discord
from discord.ext import commands 
import difflib
import aiohttp
import asyncio
import random
import asyncpg
import functools
import coroapi

class Covid(commands.Cog):
	"""Realtime covid-19 statistics"""
	def __init__(self, client):
		self.client = client
		self.corona = coroapi.Corona()
		self.countries = self.corona.countries
  
	def get_global(self):
		data = self.corona.get_global_stats()
		return data
	
	def get_country(self, country:str):
		try:
			data = self.corona.get_all_country_stats(country)
			return data
		except:
			return False
		
  
	@commands.command(aliases=['corona','covid-19','covid19'])
	async def covid(self, ctx, *,country:str=None):
		"""Get stats of a country or whole world"""
		
		gld = self.client.get_guild(700374484955299900)
		
		emj = discord.utils.get(gld.emojis, name="igloading")
		dn = discord.utils.get(gld.emojis, name="igtickmark")
		nd = discord.utils.get(gld.emojis, name="igcrossmark")
		
		embed = discord.Embed(
			color = discord.Color.gold()
		)
		
		
		if country is None:
			embed.title = "World Stats"
			thing = functools.partial(self.get_global)
			some_stuff = await self.client.loop.run_in_executor(None, thing)
			
			embed.description = some_stuff
			
			await ctx.send(embed=embed)
		else:
			if country.lower() not in self.countries:
				matches = difflib.get_close_matches(country.lower(), self.countries, 5, 0.4)
				msg = "No data found! \n"
				if len(matches) >0:
					msg += "Did you mean - \n"
					msg += "\n".join(matches)
				await ctx.send(msg)
			else:
				thing = functools.partial(self.get_country, country.lower())
				some_stuff = await self.client.loop.run_in_executor(None, thing)
				
				embed.title = country.title()
				embed.description = some_stuff
				
				await ctx.send(embed=embed)

def setup(client):
	client.add_cog(Covid(client))