import discord
from discord.ext import commands
import sqlite3
import random
import asyncio
import asyncpg

class Games(commands.Cog):
	"""Games that you can play"""
	def __init__(self, client):
		self.client = client
  
	async def ucmd(self, cmd:str):
		data = await self.client.pgdb.fetchrow("SELECT * FROM cmduse WHERE name = $1", cmd)

		if data:
			uses = data['uses'] + 1
			await self.client.pgdb.execute("UPDATE cmduse SET uses = $1 WHERE name = $2", uses, data['name'])
		else:
			await self.client.pgdb.execute("INSERT INTO cmduse(name, uses) VALUES($1, $2)", cmd, 1)
  
	async def check_user(self, id):
		res = await self.client.pgdb.fetchrow(f"SELECT * FROM cash WHERE userid = $1", id)
	
		if res:
			pass
		else:
			await self.client.pgdb.execute(f"INSERT INTO cash(userid, cash) VALUES($1, 500)", id)
		
	async def get_cash(self, id):
		res = await self.client.pgdb.fetchrow(f"SELECT cash FROM cash WHERE userid =$1", id)
		
		return res['cash']
  
	async def update_cash(self, id, cash):
		cash = await self.get_cash(id)+ cash
		await self.client.pgdb.execute(f"UPDATE cash SET cash = $1 WHERE userid = $2", cash, id)
	
	@commands.command(aliases=['cf'])
	@commands.cooldown(1, 15, commands.BucketType.user)
	async def coinflip(self, ctx, bet:str="1", *, side:str='heads'):
		"""Coinflip game."""
		await self.ucmd("coinflip")
		
		await self.check_user(ctx.author.id)
		cash = await self.get_cash(ctx.author.id)
		
		win = False
    
		gld = self.client.get_guild(700374484955299900)
		igload = discord.utils.get(gld.emojis, name="igflip")
		igwin = discord.utils.get(gld.emojis, name="igheads")
		
		iglost = discord.utils.get(gld.emojis, name="igtails")

    
		possibilities = ['heads', 'tails']
		luck = random.choice(possibilities)
		choice = ""
    
		try:
			bet = int(bet)
		except:
			bet = 1
		
		if side.lower() in ['h', 'he', 'head', 'head', 'heads']:
			choice = 'heads'
		elif side.lower() in ['t', 'ta', 'tai', 'tail', 'tails']:
			choice = 'tails'
		else:
			choice = 'heads'
		
		if bet > cash:
			await ctx.send(f"You dont have enough icash...!")
		else:
			if bet > 50000:
				bet = 50000
			else:
				if bet == 0:
					await ctx.send("You cant bet 0!")
					return
				elif bet < 0:
					await ctx.send("Negetive bets are not allowed!")
					return
				else:
					bet = bet
		
			msg = await ctx.send(f"**{ctx.author.name}** bet __{bet}__ and choose {choice} \nThe coin flipping... {str(igload)}")
      
			await asyncio.sleep(3)
      
			if choice == luck:
				win = True
				if luck == "heads":
					igmoji = igwin
				else:
					igmoji = iglost
				await msg.edit(content=f"**{ctx.author.name}** bet __{bet}__ and choose {choice} \nThe coin flipping... {str(igmoji)} and you won {bet*2}")
			else:
				win = False
				await msg.edit(content=f"**{ctx.author.name}** bet __{bet}__ and choose {choice} \nThe coin flipping... {str(iglost)} and you lost it all")
      
      
			if win:
				await self.update_cash(ctx.author.id, bet)
			else:
				await self.update_cash(ctx.author.id, -(bet))
	
	@commands.command(aliases=["s", "slot"])
	async def slots(self, ctx, bet:int=1):
		"""Slots Machine. Try your luck"""
		await self.check_user(ctx.author.id)
		gld = self.client.get_guild(700374484955299900)
		slot = discord.utils.get(gld.emojis, name="igslot")
		cash = discord.utils.get(gld.emojis, name="igcash")
		begun = discord.utils.get(gld.emojis, name="igbegun")
		bread = discord.utils.get(gld.emojis, name="igbread")
		poka = discord.utils.get(gld.emojis, name="igpoka")
		grape = discord.utils.get(gld.emojis, name="iggrape")
		frog = discord.utils.get(gld.emojis, name="igfrog")
		
		possibilities = ["win", "loose", "win", "loose", "loose", "loose", "win"]
		emojis = [cash, begun, bread, poka, grape, frog]
		
		luck = random.choice(possibilities)
		
		try:
			bet = int(bet)
		except:
			bet = 1
		c = await self.get_cash(ctx.author.id)
		
		if bet > c:
			await ctx.send(f"You dont have enough icash...!")
		else:
			if bet > 50000:
				bet = 50000
			else:
				if bet == 0:
					await ctx.send("You cant bet 0!")
					return
				elif bet < 0:
					await ctx.send("Negetive bets are not allowed!")
					return
				else:
					bet = bet
		
			msg = "= ===== =\n"
			msg += "=" + str(slot) + " " + str(slot) + " " + str(slot)+ "=\n"
			msg += "= ===== =\n"
			msg += "= ===== =\n"
			msg += "`--SLoTS--`"
			machine = await ctx.send(msg)
			
			if luck == "win":
				emoji = random.choice(emojis)
				
				await asyncio.sleep(1)
				msg = "= ===== =\n"
				msg += "=" + str(emoji) + " " + str(slot) + " " + str(slot)+ "=\n"
				msg += "= ===== =\n"
				msg += "= ===== =\n"
				msg += "`--SLoTS--`"
				await machine.edit(content=msg)
				
				await asyncio.sleep(1)
				msg = "= ===== =\n"
				msg += "=" + str(emoji) + " " + str(slot) + " " + str(emoji)+ "=\n"
				msg += "= ===== =\n"
				msg += "= ===== =\n"
				msg += "`--SLoTS--`"
				await machine.edit(content=msg)
				
				
				await asyncio.sleep(1)
				msg = "= ===== =\n"
				msg += "=" + str(emoji) + " " + str(emoji) + " " + str(emoji)+ "=\n"
				msg += "= ===== =\n"
				msg += "= ===== =\n"
				msg += f"``--SLoTS--``\n{ctx.author.name} won {bet} icash..."
				await machine.edit(content=msg)
				
				await self.update_cash(ctx.author.id, bet)
			else:
				emoji = random.choice(emojis)
				
				await asyncio.sleep(1)
				msg = "= ===== =\n"
				msg += "=" + str(emoji) + " " + str(slot) + " " + str(slot)+ "=\n"
				msg += "= ===== =\n"
				msg += "= ===== =\n"
				msg += "`--SLoTS--`"
				await machine.edit(content=msg)
				emojis.remove(emoji)
				
				await asyncio.sleep(1)
				emoji1 = random.choice(emojis)
				msg = "= ===== =\n"
				msg += "=" + str(emoji) + " " + str(slot) + " " + str(emoji1)+ "=\n"
				msg += "= ===== =\n"
				msg += "= ===== =\n"
				msg += "`--SLoTS--`"
				await machine.edit(content=msg)
				
				
				await asyncio.sleep(1)
				emoji2= random.choice(emojis)
				msg = "= ===== =\n"
				msg += "=" + str(emoji) + " " + str(emoji2) + " " + str(emoji1)+ "=\n"
				msg += "= ===== =\n"
				msg += "= ===== =\n"
				msg += f"``--SLOTS--``\n{ctx.author.name} lost {bet} icash..."
				await machine.edit(content=msg)
				
				await self.update_cash(ctx.author.id, -bet)
		
			
    
def setup(client):
	client.add_cog(Games(client))