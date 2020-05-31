import discord
from discord.ext import commands
import asyncpg
import re
import aiohttp

class Filter(commands.Cog):
	def __init__(self,client):
		self.client = client
	
	@commands.Cog.listener()
	async def on_message(self, message):
		data = await self.client.pgdb.fetchrow("SELECT * FROM guilddata WHERE guildid = $1", message.guild.id)
		state = data['nsfw']
		
		if state == "Off":
			return
		
		files = message.attachments
		
		links = re.findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", message.content)
		for link in links:
			try:
				async with aiohttp.ClientSession() as s:
					async with s.post("https://api.deepai.org/api/nsfw-detector", data={'image':link}, headers={'api-key': '2da0f0f5-361e-416e-822c-8429107891f4'}) as r:
						data = await r.json()
			except:
				pass
			if data['output']['nsfw_score'] >= 0.50:
				try:
					await message.delete()
				except:
					pass
				return
		
		for file in files:
			try:
				async with aiohttp.ClientSession() as s:
					async with s.post("https://api.deepai.org/api/nsfw-detector", data={'image':file.url}, headers={'api-key': '2da0f0f5-361e-416e-822c-8429107891f4'}) as r:
						data = await r.json()
			except:
				continue
			if data['output']['nsfw_score'] >= 0.50:
				try:
					await message.delete()
				except:
					pass
				return

def setup(client):
	client.add_cog(Filter(client))
		