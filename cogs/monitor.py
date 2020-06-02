import discord
from discord.ext import commands
import asyncpg
import asyncio
from random import randint

class Monitor(commands.Cog):
	def __init__(self, client):
		self.client = client
	
	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		before_status = before.status
		after_status = after.status
		
		after_status_name = after_status.name
		before_status_name = before_status.name
		
		
		online = [discord.Status.online, discord.Status.idle, discord.Status.dnd]
		
		# online_name = [name.name for name in online]
		
		data = await self.client.pgdb.fetch("SELECT * FROM monitor WHERE target = $1 and guild = $2", after.id, after.guild.id)
		if not data:
			return
		
		
		if after_status in online and before_status in online:
			return
		
		if after_status in online and before_status not in online:

			if data:
				for row in data:
					mentor = self.client.get_user(row['mentor'])
					target = self.client.get_user(row['target'])
					try:
						await mentor.send(f"🍏 {str(target)} is now online. ")
					except:
						await self.client.pgdb.execute("DELETE FROM monitor WHERE target = $1 and mentor = $2", row['target'], row['mentor'])
		
		if after_status not in online and before_status in online:
			if data:
				for row in data:
					mentor = self.client.get_user(row['mentor'])
					target = self.client.get_user(row['target'])
					try:
						await mentor.send(f"🍎 {str(target)} is now offline.")
					except:
						await self.client.pgdb.execute("DELETE FROM monitor WHERE target = $1 and mentor = $2", row['target'], row['mentor'])
						
	
	@commands.group(invoke_without_command=True)
	async def monitor(self, ctx):
		"""Monitor a member when they they go offline or come online you will get notified"""
		await ctx.send(f"Do `{ctx.prefix}help monitor` to get help")
	
	@monitor.command(name="delete")
	async def _dl(self, ctx, user:discord.Member):
		"""Remove monitor."""
		if user is None:
			return await ctx.send("Please speficy an user.")
		
		data = await self.client.pgdb.fetchrow("SELECT * FROM monitor WHERE target = $1 and mentor = $2", user.id, ctx.author.id)
		
		if data is None:
			return await ctx.send("You are not monitoring this user. Or you have mentioned invalid user.")
		
		await self.client.pgdb.execute("DELETE FROM monitor WHERE target =$1 and mentor =$2", data['target'], data['mentor'])
		await ctx.send("Monitor removed.")
	
	@monitor.command()
	async def add(self, ctx, user:discord.Member):
		"""Monitor someone."""
		if user is None:
			return await ctx.send("Please speficy an user.")
		
		data = await self.client.pgdb.fetchrow("SELECT * FROM monitor WHERE target = $1 and mentor = $2", user.id, ctx.author.id)
		if data:
			gld = self.client.get_guild(data['guild'])
			if gld:
				return await ctx.send("You are already monitoring this user.")
			else:
				await self.client.bot.pgdb.execute("UPDATE monitor SET guild = $1 WHERE target = $2 and mentor = $3", ctx.author.guild.id, user.id, ctx.author.id)
				await ctx.send(f"New monitor created. {str(user)}")
		
		await self.client.pgdb.execute("INSERT INTO monitor(target, mentor, guild) VALUES($1, $2,$3)", user.id, ctx.author.id, ctx.author.guild.id)
		await ctx.send(f"New monitor created. {str(user)}")
	
	@monitor.command(name="list")
	async def _ls(self, ctx):
		"""View list of your monitors"""
		data = await self.client.pgdb.fetch("SELECT * FROM monitor WHERE mentor = $1", ctx.author.id)
		
		if not data:
			return await ctx.send("You have no monitor right now.")
		
		abandon_msg = ""
		success_msg = ""
		abandon_count = 0
		success_count =0
		
		for row in data:
			try:
				target = self.client.get_user(row['target'])
				success_count +=1
				success_msg += f"{success_count}. {str(target)}\n"
			except:
				abandon_count +=1
				await self.client.pgdb.execute("DELETE FROM moitor WHERE target = $1", row['target'])
				
		
		if abandon_count > 0:
			abandon_msg = f"\n{abandon_count} nonitor deleted `Reason - Bot dont have access to that user or account not available.\n"
		
		await ctx.send(success_msg + abandon_msg)	
			

def setup(client):
	client.add_cog(Monitor(client))
		