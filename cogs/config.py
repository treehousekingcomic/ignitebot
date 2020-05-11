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

	@commands.group()
	@commands.has_permissions(administrator=True)
	async def config(self, ctx):
		"""Edit server configuration"""
		await self.ucmd("config")
		msg = ""
	
	@config.command()
	async def joinchannel(self, ctx, channel:typing.Union[discord.TextChannel, str]):
		if type(channel) == discord.TextChannel:
			data = channel.id
			msg = channel.mention + " is set for welcome welcome channel."
		elif channel == 'disable':
			data = 0
			msg = "Welcome channel disabled."
		else:
			data = 0
			msg = "Wrong argument! So I decided to disable join channel for now."
		
		await self.client.pgdb.execute("UPDATE guilddata SET wci= $1 WHERE guildid=$2", data, ctx.guild.id)
		await self.sem(ctx, "Join channel config", msg )
	
	@config.command()
	async def leavechannel(self, ctx, channel:typing.Union[discord.TextChannel, str]):
		if type(channel) == discord.TextChannel:
			data = channel.id
			msg = channel.mention + " is set for leave channel."
		elif channel == 'disable':
			data = 0
			msg = "Leave channel disabled."
		else:
			data = 0
			msg = "Wrong argument! So I decided to disable leave channel for now."
		
		await self.client.pgdb.execute("UPDATE guilddata SET bci= $1 WHERE guildid=$2", data, ctx.guild.id)
		await self.sem(ctx, "Leave channel config", msg )
	

	@config.command()
	async def warningrole(self, ctx, role:typing.Union[discord.Role, str]):
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
			msg = "Wrong argument! So I decided to remove warning role for now."
		
		await self.client.pgdb.execute("UPDATE guilddata SET wnr= $1 WHERE guildid=$2", data, ctx.guild.id)
		await self.sem(ctx, "Warning role config", msg )
	
	@config.command()
	async def leveluplog(self, ctx, channel:typing.Union[discord.TextChannel, str]):
		if type(channel) == discord.TextChannel:
			data = channel.id
			msg = channel.mention + " is set for level up log channel."
		elif channel == 'disable':
			data = 0
			msg = "Level up log disabled."
		else:
			data = 0
			msg = "Wrong argument! So I decided to disable level up log for now."
		
		await self.client.pgdb.execute("UPDATE guilddata SET lvlid= $1 WHERE guildid=$2", data, ctx.guild.id)
		await self.sem(ctx, "Level Up log config", msg )

	@config.command()
	async def autorole(self, ctx, role:typing.Union[discord.Role, str]):
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
			msg = "Wrong argument! So I decided to disable Auto role for now."
		
		await self.client.pgdb.execute("UPDATE guilddata SET wr= $1 WHERE guildid=$2", data, ctx.guild.id)
		await self.sem(ctx, "Auto role config", msg )
	
	@config.command()
	async def prefix(self, ctx, prefix:str):
		if type(prefix) == str:
			data = prefix
			msg = "`" + data + "` is the new pefix for this server."
			await self.client.pgdb.execute(f"UPDATE guilddata SET prefix= $1 WHERE guildid=$2", data, ctx.guild.id)
		else:
			msg = "Not a valid prefix. Try a new one"
	
		await self.sem(ctx, "Prefix config", msg )
	
	@config.command()
	async def welcomemessage(self, ctx, *,message:str):
		if type(message) == str and message != 'disable':
			data = message
			msg = "Welcome message updated!"
			
			await self.client.pgdb.execute(f"UPDATE guilddata SET wlcmsg= $1 WHERE guildid= $2", data, ctx.guild.id)
		elif message == 'disable':
			data = ""
			msg = "Welcome message disabled."
			
			await self.client.pgdb.execute(f"UPDATE guilddata SET wlcmsg='Null' WHERE guildid= $1", ctx.guild.id)
		else:
			data = ""
			msg = "Wrong argument! So I decided to disable welcome message for now."
		
		await self.sem(ctx, "Welcome message config", msg )

def setup(client):
	client.add_cog(SeverConfig(client))
