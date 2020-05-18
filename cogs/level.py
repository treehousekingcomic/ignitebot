import discord
from discord.ext import commands

class Level(commands.Cog):
	def __init__(self, client):
		self.client = client
  
	async def ucmd(self, cmd:str):
		data = await self.client.pgdb.fetchrow("SELECT * FROM cmduse WHERE name = $1", cmd)
  	
		if data:
			uses = data['uses'] + 1
			await self.client.pgdb.execute("UPDATE cmduse SET uses = $1 WHERE name = $2", uses, data['name'])
		else:
			await self.client.pgdb.execute("INSERT INTO cmduse(name, uses) VALUES($1, $2)", cmd, 1)
  
	async def increase_xp(self, userid:int, guildid:int, exp:int, plevel:int, user:discord.Member, ctx):
		exp = exp+5
		nlevel = int(exp ** (1/5))
		await self.client.pgdb.execute("UPDATE levels SET exp = $1 WHERE userid = $2 AND guildid = $3", exp, userid, guildid)
    
		if nlevel > plevel:
			await self.level_up(user, userid, guildid, nlevel, ctx)
		else:
			pass
		
	async def level_up(self, user:discord.Member, userid, guildid, nlevel:int, ctx):
		await self.client.pgdb.execute("UPDATE levels SET level = $1 WHERE userid = $2 AND guildid =$3", nlevel, userid, guildid)
		data = await self.client.pgdb.fetchrow("SELECT * FROM guilddata WHERE guildid = $1", guildid)
		
		if data:
			id = data['lvlid']
			chan = discord.utils.get(ctx.guild.text_channels, id=id)
			try:
				await chan.send(f"{user.mention} just advanced to level {nlevel}!")
			except:
				pass
    
    
	@commands.Cog.listener()
	async def on_message(self, message):
		try:
			data = await self.client.pgdb.fetchrow("SELECT * FROM levels WHERE userid = $1 AND guildid = $2", message.author.id, message.guild.id)
		except:
			return

		if data:
			exp = data['exp']
			level = data['level']
			
			if message.content.startswith("..") or message.author.bot == True:
				pass
			else:
				if message.author.bot !=True:
					await self.increase_xp(message.author.id, message.guild.id, exp,level, message.author, message)
		elif message.author.bot != True:
			await self.client.pgdb.execute("INSERT INTO levels(userid, guildid, exp, level) VALUES($1,$2,5,0)", message.author.id, message.guild.id)
		
		
def setup(client):
  client.add_cog(Level(client))