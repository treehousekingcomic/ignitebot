import discord
from discord.ext import commands
import aiohttp
import os
import qrcode
import random
import functools

class Utility(commands.Cog):
	"""Some utility"""
	def __init__(self, client):
		self.client = client
	
	async def ucmd(self, cmd:str):
		data = await self.client.pgdb.fetchrow("SELECT * FROM cmduse WHERE name = $1", cmd)
		
		if data:
			uses = data['uses'] + 1
			await self.client.pgdb.execute("UPDATE cmduse SET uses = $1 WHERE name = $2", uses, data['name'])
		else:
			await self.client.pgdb.execute("INSERT INTO cmduse(name, uses) VALUES($1, $2)", cmd, 1)
	
	def get_qr(self, text, fname):
		qr = qrcode.make(text)
		qr.save(f"static/qr/{fname}.png")
		
	
	@commands.command()
	@commands.cooldown(5, 600, commands.BucketType.user)
	async def genqr(self, ctx, *,text=None):
		"""Generate qr code from a text."""
		await self.ucmd("genqr")
		
		if text is None:
			return await ctx.send("Text is required.")
		
		if type(text) != str:
			try:
				text = text.name
			except:
				text = "None"

		fname = "qr"+ str(random.randint(1000,20000))
		
		# Running blocking stuff in a executor
		thing = functools.partial(self.get_qr, text, fname)
		some_stuff = await self.client.loop.run_in_executor(None, thing)
		
		file = discord.File(fp=f"static/qr/{fname}.png", filename="qr.png")
		
		await ctx.send(file=file)
		try:
			os.remove(f"static/qr/{fname}.png")
		except:
			pass
	
	@commands.command()
	async def readqr(self, ctx):
		"""Read qr code from a image."""
		await self.ucmd("readqr")
		at = ctx.message.attachments
		
		if len(at) < 1:
			return await ctx.send("Please atach an qrcode image to decode.")
		lnk = at[0].url
    
		async with aiohttp.ClientSession() as s:
			async with s.get(f"http://api.qrserver.com/v1/read-qr-code/?fileurl={lnk}") as r:
				data = await r.json()
		
		if data[0]["symbol"][0]["data"] is not None:
			await ctx.send("Data : " + data[0]["symbol"][0]["data"])
		else:
			await ctx.send("This is not a valid qr code!")
    
	
def setup(client):
	client.add_cog(Utility(client))