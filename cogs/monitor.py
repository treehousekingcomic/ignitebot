import discord
from discord.ext import commands
import asyncpg

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
		
		online_name = [name.name for name in online]
		
		data = await self.client.pgdb.fetch("SELECT * FROM monitor WHERE target = $1", after.id)
		if not data:
			return
		
		if after_status in online and before_status in online:
			return
		
		prev = await self.client.pgdb.fetchrow("SELECT * FROM monitor_helper WHERE target = $1", before.id)
		
		if prev:
			prev_status = prev['last_status']
			if prev_status == after.status.name:
				return
			else:
				await self.client.pgdb.execute("UPDATE monitor_helper SET last_status =$1 WHERE target = $2", after.status.name, after.id)
		else:
			await self.client.pgdb.execute("INSERT INTO monitor_helper(target, last_status) VALUES($1,$2)", after.id, after.status.name)
		
		if after_status in online and before_status not in online:

			if data:
				for row in data:
					mentor = self.client.get_user(row['mentor'])
					target = self.client.get_user(row['target'])
					try:
						await mentor.send(f"{str(target)} is now online. ")
					except:
						await self.client.pgdb.execute("DELETE FROM monitor WHERE target = $1 and mentor = $2", row['target'], row['mentor'])
		
		if after_status not in online and before_status in online:
			if data:
				for row in data:
					mentor = self.client.get_user(row['mentor'])
					target = self.client.get_user(row['target'])
					try:
						await mentor.send(f"{str(target)} is now offline.")
					except:
						await self.client.pgdb.execute("DELETE FROM monitor WHERE target = $1 and mentor = $2", row['target'], row['mentor'])
						
	
	@commands.group(invoke_without_command=True)
	async def monitor(self, ctx):
		"""Monitor a member"""
		await ctx.send(f"Do `{ctx.prefix}help monitor` to get help")
	
	@monitor.command()
	async def dl(self, ctx, user:discord.Member=None):
		"""Remove monitor."""
		if user is None:
			return await ctx.send("Please speficy an user.")
		
		data = await self.client.pgdb.fetchrow("SELECT * FROM monitor WHERE target = $1 and mentor = $2", user.id, ctx.author.id)
		
		if data is None:
			return await ctx.send("You are not monitoring this user")
		
		await self.client.pgdb.execute("DELETE FROM monitor WHERE target =$1 and mentor =$2", data['target'], data['mentor'])
		await ctx.send("Monitor removed.")
	
	@monitor.command()
	async def add(self, ctx, user:discord.Member=None):
		"""Monitor someone."""
		if user is None:
			return await ctx.send("Please speficy an user.")
		
		data = await self.client.pgdb.fetchrow("SELECT * FROM monitor WHERE target = $1 and mentor = $2", user.id, ctx.author.id)
		if data:
			return await ctx.send("You are already monitoring this user.")
		
		await self.client.pgdb.execute("INSERT INTO monitor(target, mentor) VALUES($1, $2)", user.id, ctx.author.id)
		await ctx.send("New monitor created.")
	
	
		
			

def setup(client):
	client.add_cog(Monitor(client))
		