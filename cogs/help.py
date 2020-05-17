import itertools
import math
from discord.ext import commands
import discord
import asyncio

class Help(commands.Cog, name="Help"):
	"""Shows help for bot"""
	def __init__(self, client):
		self.client = client
	
	async def ucmd(self, cmd:str):
		data = await self.client.pgdb.fetchrow("SELECT * FROM cmduse WHERE name = $1", cmd)
  	
		if data:
			uses = data['uses'] + 1
			await self.client.pgdb.execute("UPDATE cmduse SET uses = $1 WHERE name = $2", uses, data['name'])
		else:
			await self.client.pgdb.execute("INSERT INTO cmduse(name, uses) VALUES($1, $2)", cmd, 1)
	
		
	@commands.command(aliases=['hlp'], hidden=True)
	async def help(self, ctx, cog=None):
		"""Shows help mesaage."""
		await self.ucmd("help")
		prefix = ctx.prefix
		sg = self.client.get_guild(700374484955299900)
		
		nextbtn = discord.utils.get(sg.emojis, name="ignext")
		prevbtn = discord.utils.get(sg.emojis, name="igprev")
		skipf = discord.utils.get(sg.emojis, name="igskipf")
		skipb = discord.utils.get(sg.emojis, name="igskipb")
		beg = discord.utils.get(sg.emojis, name="igbeg")
		end = discord.utils.get(sg.emojis, name="igend")
		
		valids = [nextbtn, prevbtn]
		
		if cog is None:
			desc = ""
			cogs = []
			page = 0
			
			for cog in self.client.cogs:
				cogs.append(cog)
			
			pages = math.ceil(len(cogs)/5)
			while True:
				use = cogs[page * 5:(page*5) + 6]
				for cog in use:
					cog = self.client.get_cog(cog)
					commands = cog.get_commands()
					shown_commands = []
					for command in commands:
						if command.hidden:
							pass
						else:
							shown_commands.append(command)
				
					if len(shown_commands) > 0:
						if cog.__doc__ is None:
							doc = "No description"
						else:
							doc = cog.__doc__
					
						desc += "**__" +cog.qualified_name + "__**" + "\n`" + doc + "`\n"
				desc = f"Type `{prefix}help <category>` to get help on a cetegory. \n\n" + desc
				embed = discord.Embed(
					description=desc,
					color=ctx.author.color,
					title="Ignite Help",
					timestamp=ctx.message.created_at
				)
				embed.set_thumbnail(url=self.client.user.avatar_url)
				try:
					await msg.edit(embed=embed)
				except:
					msg = await ctx.send(embed=embed)
				
				await msg.add_reaction(prevbtn)
				await asyncio.sleep(0.1)
				await msg.add_reaction(nextbtn)
				
				def check(r,u):
				 	return (u.id == ctx.author.id) and ((r.message.id == msg.id) and r.emoji in valids)
				 
				try:
					r, u = await self.client.wait_for("reaction_add", timeout=60, check=check)
	
					if r.emoji == nextbtn:
						page +=1
						if page > pages -1:
							page = pages -1
						desc = ""
					elif r.emoji == prevbtn:
						page -= 1
						if page < 0:
							page = 0
						desc = ""

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
		else:
			cogg = self.client.get_cog(cog)
			if cogg is not None:
				desc = ''
				if cogg.__doc__ is not None:
					desc = cogg.__doc__ + "\n\n"
					
				shown_commands = []
				
				for command in cogg.get_commands():
					if command.hidden:
						pass
					else:
						shown_commands.append(command.name)
				
				if len(shown_commands)>0:
					cmds  = "Commands : `"+  ", ".join(shown_commands) + "`"
					desc += cmds
				
					embed = discord.Embed(
						title = cogg.qualified_name,
						description = desc,
						color = ctx.author.color,
						timestamp = ctx.message.created_at
					)
					embed.set_thumbnail(url=self.client.user.avatar_url)
					
					await ctx.send(embed=embed)
				else:
					await ctx.send("This command category is not available")
			else:
				cmd = self.client.get_command(cog)
				if cmd is not None:
					if cmd.hidden is False:
						desc = ""
						try:
							desc += cmd.help + "\n"
						except:
							desc += "No description provided.\n"
						if len(cmd.clean_params) > 0:
							params = []
							pr = ""
							for p in cmd.clean_params:
								params.append(p)
							for p in params:
								pr += " <" + p + ">"
							desc += "**Syntax** : `" + prefix + cmd.name + pr + "`\n"
							
						aliases = cmd.aliases
					
						if len(aliases) > 0:
							desc += "**Aliases** : " + ", ".join(aliases) + "\n"
						
						sub_cmds = []
						try:
							if len(cmd.commands)>0:
								for scmd in cmd.commands:
									sub_cmds.append(scmd)

							if len(sub_cmds ) > 0:
								desc += "\n**Subcommands** : \n"
								for scmd in sub_cmds:
									pr = ""
									for p in scmd.clean_params:
										pr += "<" + p + "> "
									desc += "`" + prefix + cmd.name + " " + scmd.name + " " + pr + "`\n"
								
						except:
							pass
						
						embed = discord.Embed(
							title = cmd.name,
							description = desc,
							color = ctx.author.color,
							timestamp = ctx.message.created_at
						)
						embed.set_thumbnail(url=self.client.user.avatar_url)
						
						await ctx.send(embed=embed)
					else:
						await ctx.send(f"No command found with the name `{cog}`.")
				else:
					await ctx.send(f"No command found with the name `{cog}`.")
				
def setup(client):
    client.add_cog(Help(client))
