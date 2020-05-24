import discord
import math
import asyncio
from discord.ext import commands

class MyHelpCommand(commands.HelpCommand):
	async def send_bot_help(self, mapping):
		ctx = self.context
		
		# Support Guild
		sg = ctx.bot.get_guild(700374484955299900)
		
		# Emoji Buttons
		nextbtn = discord.utils.get(sg.emojis, name="ignext")
		prevbtn = discord.utils.get(sg.emojis, name="igprev")
		stopbtn = discord.utils.get(sg.emojis, name="igstop")
		
		
		valids = [nextbtn, prevbtn, stopbtn]
		cogs = []
		
		for cog in ctx.bot.cogs.values():
			if await ctx.bot.is_owner(ctx.author):
				cogs.append(cog)
			else:
				cog_commands = [command for command in cog.get_commands() if command.hidden == False]
				if len(cog_commands) >0:
					cogs.append(cog)
		
		page = 0
		per_page = 5
		total_page = math.ceil(len(cogs) / per_page)
		
		while True:
			embed = discord.Embed(
				color = discord.Color.blurple(),
				timestamp = ctx.message.created_at,
				description = f"Use {self.clean_prefix}help <Category> to get help on a category\n"
			)
			now = cogs[page * per_page : page * per_page + per_page]
			#print(now)
			for cog in now:
				if await ctx.bot.is_owner(ctx.author):
					cog_commands = [command for command in cog.get_commands()]
				else:
					cog_commands = [command for command in cog.get_commands() if command.hidden == False]
				
				if len(cog_commands) > 0:
					if cog.description:
						cog_help = cog.description
					else: 
						cog_help = "No description provided"
						
					embed.description += f"**__{cog.qualified_name}__** \n`{cog_help}` \n"
				
			embed.set_thumbnail(url=ctx.bot.user.avatar_url)
			try:
				await msg.edit(embed=embed)
			except:
				msg = await ctx.send(embed=embed)
				
			await msg.add_reaction(prevbtn)
			await asyncio.sleep(0.1)
			await msg.add_reaction(stopbtn)
			await asyncio.sleep(0.1)
			await msg.add_reaction(nextbtn)
				
			def check(r,u):
				return (u.id == ctx.author.id) and ((r.message.id == msg.id) and r.emoji in valids)
				 
			try:
				r, u = await ctx.bot.wait_for("reaction_add", timeout=60, check=check)
	
				if r.emoji == nextbtn:
					page +=1
					if page > total_page -1:
						page = total_page -1
					desc = ""
				elif r.emoji == prevbtn:
					page -= 1
					if page < 0:
						page = 0
					desc = ""
				elif r.emoji == stopbtn:
					try:
						return await msg.delete()
					except:
						return

				try:
					await msg.remove_reaction(r.emoji, u)
				except:
					pass
			except:
				try:
					await msg.clear_reactions()
					break
				except:
					pass
				break
	
	# Main Help
	async def send_cog_help(self, cog):
		ctx = self.context
		pre = self.clean_prefix
		
		embed = discord.Embed(
			color = discord.Color.gold(),
			timestamp = ctx.message.created_at,
			description = f"Use {self.clean_prefix}help <command> to get help on a command. \n"
		)
		
		if await ctx.bot.is_owner(ctx.author):
				shown_commands = [command for command in cog.get_commands()]
		else:
			shown_commands = [command for command in cog.get_commands() if command.hidden == False]
			
		if len(shown_commands) == 0:
			return await ctx.send("This cog has no command.")
			
		if cog.description:
			cog_help = cog.description
		else:
			cog_help = "No description provided for this cog"
				
		embed.title = f"{cog.qualified_name}"
		embed.description += f"{cog_help} \n\nCommands : \n"
		
		for command in shown_commands:
			embed.description += f"▪︎{pre}{command.qualified_name} "
			if command.signature:
				embed.description += f"{command.signature} \n"
			else:
				embed.description += "\n"
		
		#embed.description += " - ".join(command.qualified_name for command in shown_commands)
		
		embed.set_thumbnail(url=ctx.bot.user.avatar_url)
		await ctx.send(embed=embed)
	
	# Command Help
	async def send_command_help(self, command):
		ctx = self.context
		
		embed = discord.Embed(
			color = discord.Color.green(),
			timestamp = ctx.message.created_at,
			description = ""
		)
		
		if command.hidden == True and await ctx.bot.is_owner(ctx.author) == False:
			return await ctx.send("No command found.")
		
		msg = ""
		if command.signature:
			embed.title = f"{command.qualified_name} {command.signature} \n"
		else:
			embed.title = f"{command.qualified_name}\n"
		
		if command.help:
			embed.description += f"{command.help}"
		else:
			embed.description += "No description provided\n"
		
		if len(command.aliases) > 0:
			embed.description += "Aliases : " + ", ".join(command.aliases)
		
		embed.set_thumbnail(url=ctx.bot.user.avatar_url)
		await ctx.send(embed=embed)
	
	# Group Help
	async def send_group_help(self, group):
		ctx = self.context
		pre = self.clean_prefix
		embed = discord.Embed(
			color = discord.Color.blurple(),
			timestamp = ctx.message.created_at
		)
		
		if group.signature:
			embed.title = f"{group.qualified_name} {group.signature}"
		else:
			embed.title = group.qualified_name + " - group"
		
		if group.help:
			embed.description = group.help.split("\n")[0]
		else:
			embed.description = f"No description provided."
		
		embed.description += f"\nUse `{pre}help {group.qualified_name} <sub_command>` to get help on a group command. \nSubcommands : \n"
		
		for command in group.commands:
			if command.signature:
				command_help = f"▪︎{pre}{command.qualified_name} {command.signature} \n"
			else:
				command_help = f"▪︎{pre}{command.qualified_name} \n"
			
			embed.description += command_help
		
		embed.set_thumbnail(url=ctx.bot.user.avatar_url)
		await ctx.send(embed=embed)

class Help(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.client._original_help_command = client.help_command
		client.help_command = MyHelpCommand()
		client.help_command.cog = self
	
	def cog_unload(self):
		self.client.help_command = self.client._original_help_command

def setup(client):
	client.add_cog(Help(client))