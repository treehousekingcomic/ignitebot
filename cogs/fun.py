import discord
from discord.ext import commands
import aiohttp
import json
import random

class Fun(commands.Cog):
	"""Some funny stuff."""
	def __init__(self, client):
		self.client = client
    
	async def ucmd(self, cmd:str):
		data = await self.client.pgdb.fetchrow("SELECT * FROM cmduse WHERE name = $1", cmd)
		
		if data:
			uses = data['uses'] + 1
			await self.client.pgdb.execute("UPDATE cmduse SET uses = $1 WHERE name = $2", uses, data['name'])
		else:
			await self.client.pgdb.execute("INSERT INTO cmduse(name, uses) VALUES($1, $2)", cmd, 1)
     

	@commands.command(aliases=['q','quotes'])
	@commands.cooldown(1,5,commands.BucketType.user)
	async def quote(self,ctx):
		"""Random quotes"""
      
		await self.ucmd("quote")

		sg = self.client.get_guild(700374484955299900)
		q1 = discord.utils.get(sg.emojis, name="igquote1")
		q2 = discord.utils.get(sg.emojis, name="igquote2")
		async with aiohttp.ClientSession() as s:
			async with s.get("https://api.quotable.io/random") as r:
				data = await r.json()
 
		embed = discord.Embed(colour=ctx.author.color, description=str(q1) + " " + data['content'] + " " + str(q2), timestamp=ctx.message.created_at)
		embed.set_author(name=data['author'])
		msg = await ctx.send(embed=embed)
    
	@commands.command()
	@commands.cooldown(1,5,commands.BucketType.user)
	async def meme(self, ctx):
		"""Random meme"""
		await self.ucmd("meme")

		async with aiohttp.ClientSession() as s:
			async with s.get("https://apis.duncte123.me/meme") as r:
				data = await r.json()
 
		embed = discord.Embed(colour=ctx.author.color, timestamp=ctx.message.created_at)
		embed.set_author(name=data['data']['title'], url=data['data']['url'], icon_url=self.client.user.avatar_url)
		embed.set_image(url=data['data']['image'])
		msg = await ctx.send(embed=embed)
    
	@commands.command()
	@commands.cooldown(1,5, commands.BucketType.user)
	async def joke(self, ctx):
		"""Random jokes"""
		
		await self.ucmd("joke")
		
		async with aiohttp.ClientSession() as s:
			async with s.get("https://apis.duncte123.me/joke") as r:
				data = await r.json() 
		
		await ctx.send(data['data']['title'] + "\n> " + data['data']['body'])
 
	@commands.command()
	@commands.cooldown(1,10,commands.BucketType.user)
	async def love(self, ctx, name1, name2):
		"""Love calculator"""
		
		await self.ucmd("love")
		
		async with aiohttp.ClientSession() as s:
			async with s.get(f"https://apis.duncte123.me/love/{name1}/{name2}") as r:
				data = await r.json()
				
		await ctx.send(f"Hey `{data['data']['names']}` \n>> {data['data']['score']} 💘\n\n{data['data']['message']}")
      
	@commands.command(aliases=['trans'])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def translate(self, ctx,fromlang,tolang,*,sentence:str):
		"""Translate a word or sentence"""
		await self.ucmd("translate")
		
		try:
			async with aiohttp.ClientSession() as s:
				async with s.get(f"https://viratrends.com/botscripts/wb_translate.php?zin={sentence}&fromlang={fromlang.lower()}&tolang={tolang.lower()}") as r:
					data = await r.json()

			await ctx.send(f"Original : {sentence} \nTranslated `{fromlang} to {tolang}` : {data[0]['text']}")
		except:
			await ctx.send(f"Something went wrong!")
	
	@commands.command(aliases=["pq"])
	@commands.cooldown(1,3,commands.BucketType.user)
	async def programmingquotes(self, ctx):
		"""Random programming related quotes. If you are a programmer."""
		async with aiohttp.ClientSession() as s:
			async with s.get("https://programming-quotes-api.herokuapp.com/quotes/random") as r:
				data = await r.json()
				
		embed = discord.Embed(description=data['en'], title=data['author'])
		await ctx.send(embed=embed)
	
	@commands.command()
	@commands.cooldown(1,5, commands.BucketType.user)
	async def comic(self, ctx):
		"""Random comic with pictures."""
		link = f"http://xkcd.com/{random.randint(1,2304)}/info.0.json"
		async with aiohttp.ClientSession() as s:
			async with s.get(link) as r:
				data = await r.json()
		
		desc = ""
		desc += data['transcript']
		desc+= "\n" + data['alt']
			
		embed = discord.Embed(color=ctx.author.color, description=desc, title=data['safe_title'])
		embed.set_image(url=data['img'])
		
		await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Fun(client))
