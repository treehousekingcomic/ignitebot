#pylint:disable=W0311
#pylint:disable=W0311
import discord
from discord.ext import commands
import difflib
import asyncio
import asyncpg
import math

class Tag(commands.Cog):
	"""Tags can be used to store data in your server and retrive them."""
	def __init__(self, client):
		self.client = client
	
	async def ucmd(self, cmd:str):
		data = await self.client.pgdb.fetchrow("SELECT * FROM cmduse WHERE name = $1", cmd)
		
		if data:
			uses = data['uses'] + 1
			await self.client.pgdb.execute("UPDATE cmduse SET uses = $1 WHERE name = $2", uses, data['name'])
		else:
			await self.client.pgdb.execute("INSERT INTO cmduse(name, uses) VALUES($1, $2)", cmd, 1)
	
	async def tag_exists(self, tagname, guildid):
		data = await self.client.pgdb.fetchrow("SELECT * FROM tags WHERE tagname = $1 AND guildid = $2", tagname, guildid)
		if data:
			return [True, data]
		else:
			return [False]
	
	async def tag_deletable(self, tagname, guildid):
		data = await self.client.pgdb.fetchrow("SELECT * FROM tags WHERE tagname = $1 AND guildid = $2", tagname, guildid) 
		if data:
			return True
		else:
			return False
	
	@commands.group(invoke_without_command=True)
	async def tag(self, ctx, *,tagname:str=None):
		"""Create, view delete tag."""
		if tagname is None:
			desc = "Tags are used to store some data in a guild with a name to retrive data anytime. \nType `tag create` to create a tag, `tag delete` to delete a tag and `tag <tag_name>` to view content of a tag. \nAnyone can view tags but only server admins can create tag."
			embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at, description=desc, title="Tags")
			await ctx.send(embed=embed)
		else:
			tag = await self.tag_exists(tagname, ctx.guild.id)
			if tag[0]:
				data = tag[1]
				await ctx.send(data['content'])
			else:
				await ctx.send("Tag not found!")
	
	@tag.command()
	async def list(self, ctx, page:int=1):
		sg = self.client.get_guild(700374484955299900)
		
		nextbtn = discord.utils.get(sg.emojis, name="ignext")
		prevbtn = discord.utils.get(sg.emojis, name="igprev")
		skipf = discord.utils.get(sg.emojis, name="igskipf")
		skipb = discord.utils.get(sg.emojis, name="igskipb")
		beg = discord.utils.get(sg.emojis, name="igbeg")
		end = discord.utils.get(sg.emojis, name="igend")
		
		page = page -1
		all= await self.client.pgdb.fetch("SELECT tagname FROM tags WHERE guildid = $1", ctx.guild.id)
		
		fnd = len(all)
		total_pages = math.ceil(fnd/20)
		if page > total_pages -1:
			page = total_pages-1
		if page <0:
			page = 0
		
		while True:
			offset = page * 20
			count = offset
			data = await self.client.pgdb.fetch("SELECT tagname FROM tags WHERE guildid = $1 OFFSET $2 LIMIT 20", ctx.guild.id, offset)
			msg = ""
			for row in data:
				count += 1
				msg += f"{count}. {row['tagname']} \n"
			
			embed = discord.Embed(color=ctx.author.color, description=msg, title="Tags")
			embed.set_footer(text=f"Page - {page+1}/{total_pages}")
			try:
				await mmsg.edit(embed=embed)
			except:
				mmsg = await ctx.send(embed=embed)
			
			await mmsg.add_reaction(beg)
			asyncio.sleep(0.1)
			await mmsg.add_reaction(prevbtn)
			asyncio.sleep(0.1)
			await mmsg.add_reaction(nextbtn)
			asyncio.sleep(0.1)
			await mmsg.add_reaction(end)
			
			def check(r,u):
			 	return (u.id == ctx.author.id) and (r.message.id == mmsg.id)
			 
			try:
				r, u = await self.client.wait_for("reaction_add", timeout=60, check=check)

				if r.emoji == nextbtn:
					if page + 1 > total_pages -1:
						page = total_pages -1
					else:
						page +=1
				elif r.emoji == prevbtn:
					if (page - 1) < 0:
						page = 0
					else:
						page -=1
				elif r.emoji == end:
				 	page = total_pages -1
				elif r.emoji == beg:
				 	page = 0
				try:
					await mmsg.remove_reaction(r.emoji, u)
				except:
					pass
			except:
				try:
					await mmsg.remove_reaction(r.emoji, u)
					break
				except:
					pass
				break
     
	@tag.command()
	#@commands.has_permissions(administrator=True)
	async def create(self, ctx, *, name:str=None):
		"""Create a tag"""
		reserved_words = ["create", "edit", "delete", "list", "info", "stats"]
		def check(m):
			return m.author == ctx.author and m.channel == ctx.channel
		
		ret = await self.tag_exists(name, ctx.guild.id)
		if ret[0]:
			await ctx.send("A tag with that name already exists")
		else:
			if name is not None:
				name_part = name.split(" ")[0]
				if name_part in reserved_words:
					return await ctx.send("This name contains reserved word.")
				await ctx.send(f"Ok! The name will be `{name}`.. Write some contents! You have 60 seconds.")
				askmsg = await self.client.wait_for('message', timeout=60, check=check)
				con = askmsg.content
				if con.lower() in ["cancel", "stop", "abort"]:
					await ctx.send("Tag creation cancelled!")	
				else:	
					await self.client.pgdb.execute("INSERT INTO tags(tagname, content, userid, guildid, ttp) VALUES($1, $2,$3, $4, $5)", name, con, ctx.author.id, ctx.guild.id, "free")
					await ctx.send("Tag created.")
	
	@tag.command(name="edit")
	async def tag_edit(self, ctx, *,name:str=None):
		"""Edit a tag"""
		
		def check(m):
			return m.author == ctx.author and m.channel == ctx.channel

		if name is None:
			return await ctx.send("Please specify a tag name.")
		
		tag = await self.tag_exists(name, ctx.guild.id)
		if tag[0]:
			await ctx.send(f"Editing `{name}`.. Write new contents! You have 60 seconds.")
			askmsg = await self.client.wait_for('message', timeout=60, check=check)
			con = askmsg.content
			if con.lower() in ["cancel", "stop", "abort"]:
				await ctx.send("Tag editing cancelled!")	
			else:	
				await self.client.pgdb.execute("UPDATE tags SET content = $1 WHERE userid = $2 AND tagname =$3 AND guildid = $4", con, ctx.author.id, name, ctx.guild.id)
				await ctx.send("Tag editted.")
		else:
			await ctx.send(f"This tag doesn't exists. `{name}`")
		
	@tag.command(name="info")
	async def _tag_info(self, ctx, *, name:str=None):
		"""View info of a tag"""
		embed = discord.Embed(
			color = discord.Color.blurple(),
			description = ""
		)
		if name is None:
			return await ctx.send("Please specify a tag name.")
		
		tag = await self.tag_exists(name, ctx.guild.id)
		if tag[0]:
			embed.title = tag[1]['tagname']
			try:
				creator = ctx.guild.get_member(tag[1]['userid'])
			except:
				creator = None
			if creator:
				embed.description += f"Created by {str(creator)}"
			else:
				embed.description = "The owner of this server is not in this server."
			
			await ctx.send(embed=embed)
		else:
			await ctx.send(f"This tag doesn't exists. `{name}`")
		
	@tag.command(name="delete")
	#@commands.has_permissions(administrator=True)
	async def delete_tag(self, ctx, *,name:str=None):
		"""Delete a tag"""
		dt = await self.tag_exists(name, ctx.guild.id)
		if dt[0]:
			
			if ctx.author.guild_permissions.administrator:
				pass
			elif dt[1]['userid'] == ctx.author.id:
				pass
			else:
				return await ctx.send("You cant delete this tag.")	
			
			gld = self.client.get_guild(700374484955299900)
			tickemoji = discord.utils.get(gld.emojis, name="igtickmark")
			crossmoji = discord.utils.get(gld.emojis, name="igcrossmark")
						
			msg = await ctx.send("⚠️ | Are you sure?")
              
			await msg.add_reaction(tickemoji)
			await asyncio.sleep(0.5)
			await msg.add_reaction(crossmoji)
					
			def check(r, u):
				return (u.id == ctx.author.id) and (r.message.id == msg.id)
			try:
				r, u = await self.client.wait_for('reaction_add',timeout=20,check=check)
						
				if r.emoji.name == 'igtickmark':
					await self.client.pgdb.execute("DELETE FROM tags WHERE tagname = $1 AND guildid = $2", name, ctx.guild.id)
					await msg.delete()
					await ctx.send("🗑 | Tag deleted!")
				else:
					await msg.delete()
			except:
				await msg.delete()
				await ctx.send("🕝 | Timeout!")
		else:
			await ctx.send(f"The tag doesn't exists. `{name}`")
	
	@tag.command(name="claim")
	async def claim_tag(self, ctx, *, name:str=None ):
		"""Claim a tag if there is no owner of that tag."""
		if name is None:
			return await ctx.send("Please specify a tag name.")
		
		tag = await self.tag_exists(name, ctx.guild.id)
		if tag[0]:
			creator = ctx.guild.get_member(tag[1]['userid'])
			if creator is None:
				await self.client.pgdb.execute("UPDATE tags SET userid = $1 WHERE tagname = $2 AND guildid = $3",  ctx.author.id, name, ctx.guild.id)
				await ctx.send("Tag claimed.")
			else:
				return await ctx.send("Tag owner is still in this server.")
		else:
			await ctx.send(f"The tag doesn't exists. `{name}`")
	
	@tag.command(name="transfer")
	async def tag_trans(self, ctx, name:str=None, member:discord.Member=None):
		"""Transfer tag to someone else"""
		if member is None or name is None:
			return await ctx.send("Tag name and member both is required.")
		
		tag = await self.tag_exists(name, ctx.guild.id)
		if tag[0]:
			creator = ctx.guild.get_member(tag[1]['userid'])
			if creator == ctx.author:
				await self.client.pgdb.execute("UPDATE tags SET userid = $1 WHERE tagname = $2 AND guildid = $3",  member.id, name, ctx.guild.id)
				await ctx.send("Tag transfered.")
			else:
				return await ctx.send("You are not the owner of this tag.")
		else:
			await ctx.send(f"The tag doesn't exists. `{name}`")
	
	@tag.command(name="search")
	async def tag_search(self, ctx, *,query:str=None):
		if query is None:
			return await ctx.send("Query is required.")
		page = 0
		sg = self.client.get_guild(700374484955299900)
		
		nextbtn = discord.utils.get(sg.emojis, name="ignext")
		prevbtn = discord.utils.get(sg.emojis, name="igprev")
		skipf = discord.utils.get(sg.emojis, name="igskipf")
		skipb = discord.utils.get(sg.emojis, name="igskipb")
		beg = discord.utils.get(sg.emojis, name="igbeg")
		end = discord.utils.get(sg.emojis, name="igend")
		
		page = page -1
		all= await self.client.pgdb.fetch("SELECT tagname FROM tags WHERE guildid = $1", ctx.guild.id)
		
		fnd = len(all)
		total_pages = math.ceil(fnd/20)
		if page > total_pages -1:
			page = total_pages-1
		if page <0:
			page = 0
		
		while True:
			offset = page * 20
			count = offset
			data = await self.client.pgdb.fetch("SELECT tagname FROM tags WHERE guildid = $1 AND to_tsvector(tagname) @@ to_tsquery($2) OFFSET $3 LIMIT 20", ctx.guild.id,query, offset)
			
			if data:
				if len(data) <= 0:
					return await ctx.send("No result.")
			if not data:
				return await ctx.send("No result.")
			msg = ""
			for row in data:
				count += 1
				msg += f"{count}. {row['tagname']} \n"
			
			embed = discord.Embed(color=ctx.author.color, description=msg, title="Tag search")
			embed.set_footer(text=f"Page - {page+1}/{total_pages}")
			try:
				await mmsg.edit(embed=embed)
			except:
				mmsg = await ctx.send(embed=embed)
			
			await mmsg.add_reaction(beg)
			asyncio.sleep(0.1)
			await mmsg.add_reaction(prevbtn)
			asyncio.sleep(0.1)
			await mmsg.add_reaction(nextbtn)
			asyncio.sleep(0.1)
			await mmsg.add_reaction(end)
			
			def check(r,u):
			 	return (u.id == ctx.author.id) and (r.message.id == mmsg.id)
			 
			try:
				r, u = await self.client.wait_for("reaction_add", timeout=60, check=check)

				if r.emoji == nextbtn:
					if page + 1 > total_pages -1:
						page = total_pages -1
					else:
						page +=1
				elif r.emoji == prevbtn:
					if (page - 1) < 0:
						page = 0
					else:
						page -=1
				elif r.emoji == end:
				 	page = total_pages -1
				elif r.emoji == beg:
				 	page = 0
				try:
					await mmsg.remove_reaction(r.emoji, u)
				except:
					pass
			except:
				try:
					await mmsg.remove_reaction(r.emoji, u)
					break
				except:
					pass
				break
		
def setup(client):
  client.add_cog(Tag(client))