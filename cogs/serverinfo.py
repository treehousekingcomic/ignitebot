import discord
import os
from discord.ext import commands
from discord.utils import get
import aiohttp
import random
import asyncpg
from PIL import Image, ImageDraw
import math
from datetime import datetime, timedelta

class ServerInfo(commands.Cog, name="Server"):
	"""Get server information."""
	def __init__(self, client):
		self.client = client
    
	async def ucmd(self, cmd:str):
		data = await self.client.pgdb.fetchrow("SELECT * FROM cmduse WHERE name = $1", cmd)
  	
		if data:
			uses = data['uses'] + 1
			await self.client.pgdb.execute("UPDATE cmduse SET uses = $1 WHERE name = $2", uses, data['name'])
		else:
			await self.client.pgdb.execute("INSERT INTO cmduse(name, uses) VALUES($1, $2)", cmd, 1)
	
	@commands.command(aliases=['lb'])
	async def leaderboard(self, ctx, flag:str="server"):
		"""Learderboard of your server according to their XP"""
		await self.ucmd("leaderboard")
		if flag == "server":
			members = ctx.guild.members
			lb = ctx.guild.name
			
			data = await self.client.pgdb.fetch("SELECT * FROM levels WHERE guildid = $1 ORDER BY exp DESC LIMIT 10", ctx.guild.id)
		elif flag == "global":
			members = self.client.users
			lb = "Global"
			data = await self.client.pgdb.fetch("SELECT * FROM levels ORDER BY exp DESC LIMIT 10")
		else:
			flag = "server"
			members = ctx.guild.members
			lb = ctx.guild.name
			data = await self.client.pgdb.fetch("SELECT * FROM levels WHERE guildid = $1 ORDER BY exp DESC LIMIT 10", ctx.guild.id)
			
		
		msg = ""
		count = 0
		
		for row in data:
			try:
				if flag == "server":
					member = ctx.guild.get_member(row['userid'])
					dd = await self.client.pgdb.fetchrow("SELECT * FROM levels WHERE guildid = $1 and userid =$2 ORDER BY exp DESC LIMIT 10", ctx.guild.id, member.id)
					xp = dd['exp']
					level = dd['level']
				else:
					member = self.client.get_user(row['userid'])
					
					dd = await self.client.pgdb.fetch("SELECT * FROM levels WHERE userid= $1", member.id)
					xp = 0
					level = 0
					for d in dd:
						xp += d['exp']
						level += d['level']
				if member.bot != True:
					count += 1
				
				if count == 1:
					pre = "🥇"
				elif count == 2:
					pre = "🥈"
				elif count == 3:
					pre = "🥉"
				else:
					pre = ""
				
				if pre == "":
					txt = count
				else:
					txt = pre
				msg += f"{txt}. **{str(member)}** `Level {level} - Xp {xp}`\n"
			except:
				pass

		embed = discord.Embed(colour=ctx.author.color, description=msg, timestamp=ctx.message.created_at)
		embed.set_author(name=f"{lb} - Leaderboard", icon_url=ctx.guild.icon_url)
		await ctx.send(embed=embed)
	
	@commands.command(aliases=['serverstatus', 'sinfo', 'si'])
	async def serverinfo(self, ctx):
		"""Server information"""
		await self.ucmd("serverinfo")
		members = ctx.guild.member_count
		total_online_members = 0
		online_members = 0
		idle_members = 0
		dnd_members = 0
		offline_members = 0
		bots = 0
        
		sg = self.client.get_guild(700374484955299900)
		igidle = discord.utils.get(sg.emojis, name="igidle")
		igonline = discord.utils.get(sg.emojis, name="igonline")
		igoffline = discord.utils.get(sg.emojis, name="igoffline")
		igdnd = discord.utils.get(sg.emojis, name="igdnd")
        
		#print(ctx.guild.owner.name)
		status_list = [discord.Status.online, discord.Status.idle, discord.Status.dnd, discord.Status.invisible]
		
		for member in ctx.guild.members:
			if member.bot == True:
				bots += 1

		for member in ctx.guild.members:
			if member.status == discord.Status.idle:
				idle_members += 1

		for member in ctx.guild.members:
			if member.status == discord.Status.dnd:
				dnd_members += 1

		for member in ctx.guild.members:
			if member.status == discord.Status.offline:
				offline_members += 1
		
		for member in ctx.guild.members:
			if member.status == discord.Status.online:
				online_members += 1


		embed = discord.Embed(colour=ctx.author.color, timestamp=ctx.guild.created_at)
		embed.set_author(name=f"{ctx.guild.name}")
		embed.set_thumbnail(url=ctx.guild.icon_url)
        
		embed.add_field(name="Owner", value=ctx.guild.owner, inline=False)
		embed.add_field(name="Id", value=ctx.guild.id, inline=False)
		embed.add_field(name="Channels", value=f"🔊 {len(ctx.guild.voice_channels)}\n#️⃣ {len(ctx.guild.text_channels)}", inline=False)
		embed.add_field(name="Members", value=f"{str(igonline)} {online_members} {str(igidle)} {idle_members} {str(igdnd)} {dnd_members} {str(igoffline)} {offline_members}\nTotal members : {members}", inline=False)
		embed.add_field(name="Roles", value=len(ctx.guild.roles), inline=False)
		embed.add_field(name="Emojis", value=f"{len(ctx.guild.emojis)}/{ctx.guild.emoji_limit}",inline=False)
		embed.set_footer(text="created")
        
		await ctx.send(embed=embed)
		# embed.add_field(name="Joined at", value=ctx.author.joined_at.strftime('%a, %#d %B %Y, %I:%M %p UTC'))
	
	@commands.command()
	async def logo(self,ctx):
		"""Get server logo"""
		await self.ucmd("logo")
		async with aiohttp.ClientSession() as s:
			async with s.get(str(ctx.guild.icon_url)) as r:
				data = await r.read()
      
		fname = "static/logos/" + ctx.guild.name.replace(" ","_") + str(random.randint(1,10000)) + ".png"
      
		with open(fname, 'wb') as f:
			f.write(data)
      
		file = discord.File(fp=fname, filename="icon.png")
		await ctx.send(file=file)
		os.remove(fname)
	
	@commands.group(invoke_without_command=True)
	@commands.has_permissions(manage_guild=True)
	async def serverbg(self, ctx):
		"""Change the background image of profile/rank card. `serverbg reset` Will reset it to default"""
		await self.ucmd("serverbg")
		fname = f"static/img/{ctx.guild.id}.png"
		
		if len(ctx.message.attachments) >0:
			if ctx.message.attachments[0].filename.endswith("jpg") or ctx.message.attachments[0].filename.endswith("png") or ctx.message.attachments[0].filename.endswith("jpeg"):
				await ctx.message.attachments[0].save(fname)
				bg = Image.open(fname)
				width, height = bg.size
				if width == 900 and height == 238:
					await ctx.send("Rank card image changed.")
				else:
					x1 = 0
					y1 = 0
					x2 = width
					nh = math.ceil(width *0.264444)
					y2 = 0

					if nh < height:
						y1 = (height / 2) -119
						y2 = nh + y1
						
					newbg = bg.crop((x1,y1,x2,y2))
					newbg = newbg.resize((900,238))
					newbg.save(fname)
					await ctx.send(f"The image you gave is not suitable for card. 900x238 is perfect so i cropped it. See profile now. ")
			else:
				await ctx.send("Only `jpg` or `png` is supported.")
		else:
			await ctx.send("No file please attach a image file. (900x238)")
	
	@serverbg.command()
	async def reset(self, ctx):
		try:
			os.remove(f"static/img/{ctx.guild.id}.png")
			await ctx.send("Rank card background restored to default!")
		except:
			await ctx.send("You dont have custom rank card background!")
	
	@commands.group(invoke_without_command=True)
	async def premium(self, ctx):
		"""Check if server is premium or not"""
		result = await self.client.pgdb.fetchrow("SELECT * FROM keys WHERE guildid = $1", ctx.guild.id)
		if result:
			return await ctx.send("This server enjoying Ignite Premium. 🎉")
		else:
			return await ctx.send("This server is not subscribed to premium. Join the official server to get premium.")
	
	@premium.command(aliases=['stats', 'duration'])
	async def status(self, ctx):
		"""Check duration/status of membership"""
		result = await self.client.pgdb.fetchrow("SELECT * FROM keys WHERE guildid = $1", ctx.guild.id)
		
		if result:
			valid_till = result['valid_till']
			delta = valid_till - datetime.now() 
			
			dur = ""
			days = delta.days
			seconds = delta.seconds
			
			year = 0
			month = 0
			day = 0
			hour = 0
			minute = 0
			second = 0
			
			if days >= 365:
				year = days//365	
				days = days%365
				
			
			if days >=30:
				month = days//30
				
				if month >= 12:
					year += month // 12
					
					month = month % 12
				
				days = days %30
					
			if days > 0:
				day = days
				
			if seconds > 3600:
				hour = seconds//3600	
				seconds = seconds%3600
			
			if seconds >= 60:
				minute = seconds//60
				
				seconds = seconds%60
			
			if seconds > 0:
				second = seconds
				
			dur = f"{f'{year} Years ' if year > 0 else ''}{f'{month} Months ' if month > 0 else ''}{f'{day} Days ' if day > 0 else ''}{f'{hour} Hours ' if hour > 0 else ''}{f'{minute} Minutes ' if minute > 0 else ''}{f'{second} Seconds ' if second > 0 else ''}"
				
			await ctx.send(f"Premium membership of this server will expire in **{dur}**")
		
def setup(client):
    client.add_cog(ServerInfo(client))
