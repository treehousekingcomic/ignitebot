import discord
import json
import typing
import os
import pprint
from discord.ext import commands
from discord.utils import get
import sqlite3
import asyncpg

class SeverConfig(commands.Cog, name="Config"):
	"""Edit server configuration."""
	def __init__(self, client):
		self.client = client
  
	async def ucmd(self, cmd:str):
		data = await self.client.pgdb.fetchrow("SELECT * FROM cmduse WHERE name = $1", cmd)
  	
		if data:
			uses = data['uses'] + 1
			await self.client.pgdb.execute("UPDATE cmduse SET uses = $1 WHERE name = $2", uses, data['name'])
		else:
			await self.client.pgdb.execute("INSERT INTO cmduse(name, uses) VALUES($1, $2)", cmd, 1)
	
	async def sem(self, ctx, title, des):
		embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at, description=des)
		embed.set_author(name=title, icon_url=self.client.user.avatar_url)
		
		await ctx.send(embed=embed)

	@commands.group(invoke_without_command = True)
	@commands.has_permissions(administrator=True)
	async def config(self, ctx):
		"""Edit server configuration"""
		await self.ucmd("config")
		return await ctx.send(f"Do `{ctx.prefix}help config` to see available commands.")
	
	@config.command()
	async def joinchannel(self, ctx, channel:typing.Union[discord.TextChannel, str]=None):
		"""Setup welcome/join channel"""
		
		if channel is None:
			return await ctx.send("Please mention a text-channel")
		
		if type(channel) == discord.TextChannel:
			data = channel.id
			msg = channel.mention + " is set for welcome welcome channel."
		elif channel == 'disable':
			data = 0
			msg = "Welcome channel disabled."
		else:
			return await ctx.send("Wrong argument! Please mention a text channel where I can send messsge.")
		
		await self.client.pgdb.execute("UPDATE guilddata SET wci= $1 WHERE guildid=$2", data, ctx.guild.id)
		await self.sem(ctx, "Join channel config", msg )
	
	@config.command()
	async def leavechannel(self, ctx, channel:typing.Union[discord.TextChannel, str]=None ):
		"""Setup leave/bye bye channel"""
		
		if channel is None:
			return await ctx.send("Please mention a channel.")
		
		if type(channel) == discord.TextChannel:
			data = channel.id
			msg = channel.mention + " is set for leave channel."
		elif channel == 'disable':
			data = 0
			msg = "Leave channel disabled."
		else:
			data = 0
			return await ctx.send("Wrong argument! Please mention a text channel where I can send message")
		
		await self.client.pgdb.execute("UPDATE guilddata SET bci= $1 WHERE guildid=$2", data, ctx.guild.id)
		await self.sem(ctx, "Leave channel config", msg )
	

	@config.command()
	async def warningrole(self, ctx, role:typing.Union[discord.Role, str]=None ):
		"""Setup warning role."""
		
		if role is None:
			return await ctx.send("Please mention a role.")
		
		if type(role) == discord.Role:
			data = role.id
			if role.managed is False:
				msg = role.mention + " is set for Warning role."
			else:
				data = 0
				msg = "This role is automatically managed. Cant be aggigned to anyone else."
		elif role == 'disable':
			data = 0
			msg = "Warning role removed"
		else:
			data = 0
			return await ctx.send("Wrong argument! Please mention a role lower than me. If the role is higher than me then drag my role up.")
		
		await self.client.pgdb.execute("UPDATE guilddata SET wnr= $1 WHERE guildid=$2", data, ctx.guild.id)
		await self.sem(ctx, "Warning role config", msg )
	
	@config.command()
	async def leveluplog(self, ctx, channel:typing.Union[discord.TextChannel, str]=None ):
		"""Setup level up log channel"""
		
		if channel is None:
			return await ctx.send("Please mention a channel")
		
		if type(channel) == discord.TextChannel:
			data = channel.id
			msg = channel.mention + " is set for level up log channel."
		elif channel == 'disable':
			data = 0
			msg = "Level up log disabled."
		else:
			data = 0
			return await ctx.send("Wrong argument! Please mention a text channel where I can send message")
		
		await self.client.pgdb.execute("UPDATE guilddata SET lvlid= $1 WHERE guildid=$2", data, ctx.guild.id)
		await self.sem(ctx, "Level Up log config", msg )

	@config.command()
	async def autorole(self, ctx, role:typing.Union[discord.Role, str]=None ):
		"""Add role to a member"""
		
		if role is None:
			return await ctx.send("Role is required.")
		
		if type(role) == discord.Role:
			data = role.id
			if role.managed is False:
				msg = role.mention + " is set for Auto role."
			else:
				data = 0
				msg = "This role is automatically managed. Cant be assigned to anyone else."
		elif role == 'disable':
			data = 0
			msg = "Auto role disabled"
		else:
			data = 0
			return await ctx.send("Wrong argument! Please mention a role that you want to assign to new members.")
		
		await self.client.pgdb.execute("UPDATE guilddata SET wr= $1 WHERE guildid=$2", data, ctx.guild.id)
		await self.sem(ctx, "Auto role config", msg )
	
	@config.command()
	async def prefix(self, ctx, prefix:str=None ):
		"""Change prefix for your server"""
		
		if prefix is None:
			return await ctx.send("New prefix is required.")
		
		if type(prefix) == int:
			prefix = str(prefix)
		if type(prefix) == str:
			data = prefix
			msg = "`" + data + "` is the new pefix for this server."
			await self.client.pgdb.execute(f"UPDATE guilddata SET prefix= $1 WHERE guildid=$2", data, ctx.guild.id)
		else:
			msg = "Not a valid prefix. Try a new one"
	
		await self.sem(ctx, "Prefix config", msg )
	
	@config.command()
	async def welcomemessage(self, ctx, *,message:str=None):
		"""Setup a welcome message"""
		
		if message is None:
			return await ctx.send("Message is required.")
		
		if type(message) == str and message != 'disable':
			data = message
			msg = "Welcome message updated!"
			
			await self.client.pgdb.execute(f"UPDATE guilddata SET wlcmsg= $1 WHERE guildid= $2", data, ctx.guild.id)
		elif message == 'disable':
			data = ""
			msg = "Welcome message disabled."
			
		await self.client.pgdb.execute(f"UPDATE guilddata SET wlcmsg='Null' WHERE guildid= $1", ctx.guild.id)
		
		await self.sem(ctx, "Welcome message config", msg )
	
	@commands.group(invoke_without_command=True)
	async def blacklist(self, ctx):
		"""Add member in blacklist to prevent him spamming your server. Similar to `mute` but by adding him in blacklist you are preventing him from leaving and rejoining to get rid of warning role."""
		return await ctx.send("Add a member in your server blacklist to prevent him spamming your server. Make sure you setup warning role correctly")
	
	@blacklist.command()
	@commands.has_permissions(manage_guild=True)
	async def add(self, ctx, member:discord.Member=None, *, reason:str="None"):
		"""Add member in blacklist"""
		
		if member is None:
			return await ctx.send("Please mention a member.")
		
		wres = await self.client.pgdb.fetchrow("SELECT * FROM guilddata WHERE guildid = $1", ctx.guild.id)
		blstatus = await self.client.pgdb.fetchrow("SELECT * FROM blacklist WHERE userid = $1 AND guildid = $2", member.id, ctx.guild.id)
		
		if blstatus:
			return await ctx.send("This member is already in blacklist.")
		
		if len(reason) > 200:
			return await ctx.send("Reason cant be bigger than 200 characters")
		
		for role in member.roles:
			try:
				await member.remove_roles(role)
			except:
				pass
		
		role = discord.utils.get(ctx.guild.roles, id=wres['wnr'])
		
		if role is None:
			return await ctx.send(f"Cant find a warning role. Make sure to add that. check `{ctx.prefix}help config` to see how you can add warning role. Then try again")
		
		if role:
			try:
				await member.add_roles(role)
				await ctx.send(f"Successfully added {str(member)} in blacklist")
				await self.client.pgdb.execute("INSERT INTO blacklist(userid, guildid, reason) VALUES($1, $2, $3)", member.id, ctx.guild.id, reason)
			except commands.MissingPermissions:
				return await ctx.send(f"Unable to add {str(member)} in blacklist. Make sure the warning role is lower than my top role. And I have `manage roles` permission. Its highly recommended to give me the Administrator permission and keep my role on top of other memebrs top role. so I can work smothly")
		else:
			return await ctx.send(f"Cant find a warning role. Make sure to add that. check `{ctx.prefix}help config` to see how you can add warning role. Then try again")
	
	@blacklist.command()
	@commands.has_permissions(manage_guild=True)
	async def remove(self, ctx, member:discord.Member=None):
		"""Remove member from blacklist"""
		
		if member is None:
			return await ctx.send("Please mention a member.")
		
		wres = await self.client.pgdb.fetchrow("SELECT * FROM guilddata WHERE guildid = $1", ctx.guild.id)
		blstatus = await self.client.pgdb.fetchrow("SELECT * FROM blacklist WHERE userid = $1 AND guildid = $2", member.id, ctx.guild.id)
		
		if not blstatus:
			return await ctx.send("This member is not in blacklist.")
		
		role = discord.utils.get(ctx.guild.roles, id=wres['wnr'])
		
		if role is None:
			return await ctx.send(f"Cant find a warning role. Make sure to add that. check `{ctx.prefix}help config` to see how you can add warning role. Then try again")
		
		if role:
			try:
				await member.remove_roles(role)
				await ctx.send(f"Successfully removed {str(member)} from blacklist")
				await self.client.pgdb.execute("DELETE FROM blacklist WHERE userid = $1 AND guildid = $2", member.id, ctx.guild.id)
			except commands.MissingPermissions:
				return await ctx.send(f"Unable to add {str(member)} in blacklist. Make sure the warning role is lower than my top role. And I have `manage roles` permission. Its highly recommended to give me the Administrator permission and keep my role on top of other memebrs top role. so I can work smothly")
		else:
			return await ctx.send(f"I was unable to remove this member from blacklist. Make sure i have `Manage roles` permission and my top role is higher than his role.")

def setup(client):
	client.add_cog(SeverConfig(client))
