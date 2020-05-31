import discord
from discord.ext import commands

class Counting(commands.Cog):
	def __init__(self, client):
		self.client = client
    
    
	@commands.Cog.listener()
	async def on_message(self, message):
		if message.channel.id == 715768243758956564:
			ls = []
			async for msg in message.channel.history(limit=2):
				ls.append(msg)
			try:
				examine = ls[1]
			except:
				examine = ls[0]
			if examine.author == message.author:
				await message.delete()
				return
			
			# Is a float or not
			try:
				cont = str(examine.content)
				cont_ls = cont.split(".")
				if len(cont_ls) > 1:
					await message.delete()
					return
			except:
				pass
			
			# Getting int
			try:
				last_num = int(examine.content)
			except:
				return await message.delete()
				
			next_num = last_num + 1
			
			try:
				if next_num == int(message.content):
					pass
				else:
					await message.delete()	
			except:
				await message.delete()
		
def setup(client):
  client.add_cog(Counting(client))