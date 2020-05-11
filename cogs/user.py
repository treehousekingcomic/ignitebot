import discord
from discord.ext import commands
import aiohttp
import asyncio
import extcolors
import os
import math
from PIL import Image, ImageDraw, ImageFont
import random
import asyncpg

class User(commands.Cog):
	"""Some user accessories"""
	def __init__(self, client):
		self.client = client
	
	async def ucmd(self, cmd:str):
		data = await self.client.pgdb.fetchrow("SELECT * FROM cmduse WHERE name = $1", cmd)
		
		if data:
			uses = data['uses'] + 1
			await self.client.pgdb.execute("UPDATE cmduse SET uses = $1 WHERE name = $2", uses, data['name'])
		else:
			await self.client.pgdb.execute("INSERT INTO cmduse(name, uses) VALUES($1, $2)", cmd, 1)
	
	@commands.command(aliases=['uinfo', 'uinf'])
	async def userinfo(self, ctx, member: discord.Member=None):
		"""Get info of a user"""
		await self.ucmd("userinfo")
		if member is None:
			member = ctx.author
		
		embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)
		embed.set_author(name=f"User Info - {member.name}")
		embed.set_thumbnail(url=member.avatar_url)

		embed.add_field(name="ID", value=member.id, inline=False)
		embed.add_field(name="Guild Name", value=member.display_name, inline=False)
		embed.add_field(name="Created at", value=member.created_at.strftime('%a, %#d %B %Y, %I:%M %p UTC'), inline=False)
		embed.add_field(name="Joined at", value=member.joined_at.strftime('%a, %#d %B %Y, %I:%M %p UTC'), inline=False)
		embed.set_footer(text=f"Requested by - {ctx.author.name}", icon_url=ctx.author.avatar_url)
			
		await ctx.send(embed=embed)
    
	@commands.command(aliases=['image', 'av'])
	async def avatar(self, ctx, member:discord.Member=None):
		"""Get avatar/picture of a user"""
		await self.ucmd("avatar")
		if member is None:
			member = ctx.author
		embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)
		embed.set_author(name=member.name)
		embed.set_image(url=member.avatar_url)
		await ctx.send(embed=embed)
	
	@commands.command(aliases=["rank"])
	async def profile(self, ctx):
		"""Nice profile card. Shows level, xp, rank and status"""
		await self.ucmd("profile")
		res = await self.client.pgdb.fetch(f"SELECT * FROM levels WHERE guildid = $1 ORDER BY exp DESC", ctx.guild.id)
		pos = 0;
		xp = 0;
		level = 0;
		
		for result in res:
			pos+=1
			if result['userid'] == ctx.author.id:
				xp = result['exp']
				level = result['level']
				break;
			else:
				pass
		
		if level >0:
			lnk = str(ctx.author.avatar_url_as(format="png"))
			async with aiohttp.ClientSession() as s:
				async with s.get(lnk) as r:
					data = await r.read()
			
			imn = f"static/profile/{ctx.author.id}.png"
			with open(imn,'wb') as f:
				f.write(data)
			
			pro = Image.open(imn)
			npro = pro.resize((180,180))
			npro = npro.convert("RGBA")
			os.remove(imn)
			
			try:
				card = Image.open(f"static/img/{ctx.guild.id}.png")
				card = card.convert("RGBA")
			except:
				card = Image.open(f"static/profile/card3.png")
				card = card.convert("RGBA")
			
			if ctx.author.status == discord.Status.online:
				ostatus = "online"
			elif ctx.author.status == discord.Status.idle:
				ostatus = "idle"
			elif ctx.author.status == discord.Status.dnd:
				ostatus = "dnd"
			else:
				ostatus = "offline"
      
			# User status based badge
			status = Image.open(f"static/profile/{ostatus}.png")
			status = status.convert("RGBA")
			status = status.resize((30,30))
      
			leveli = Image.open("static/profile/level.png")
			ranki = Image.open("static/profile/rank.png")
			leveli = leveli.resize((20,20))
			ranki = ranki.resize((25,25))
			xpi = Image.open("static/profile/xp.png")
			xpi = xpi.resize((25,25))
      
      	  # Section A-2 
            # A blank profile picture holder
			profile_pic_holder = Image.new("RGBA",card.size, (255,255,255,0)) # Is used for a blank image so that i can mask
      
      	  # Mask to crop image
			mask = Image.new("RGBA", card.size, 0)
			mask_draw = ImageDraw.Draw(mask)
			mask_draw.ellipse((29, 29, 209, 209), fill=(255,25,255,255)) # The part need to be cropped
      
            # Editing stuff here
      
            # ======== Fonts to use =============
			font_normal = ImageFont.truetype("static/profile/font.ttf", 36)
			font_small = ImageFont.truetype("static/profile/font.ttf", 20)
			font_signa = ImageFont.truetype("static/profile/font3.ttf",25)
      
            # ======== Colors ========================
			WHITE = (189, 195, 199)
			DARK = (252, 179, 63)
			YELLOW = (255, 234, 167)
      
			def get_str(xp):
				if xp <1000:
					return str(xp)
				if xp >= 1000 and xp < 1000000:
					return str(round(xp/1000,1))  + "k"
				if xp > 1000000:
					return str(round(xp/1000000,1))+"M"
      
      	   # ======== Drawing texts on card =========
			draw = ImageDraw.Draw(card)
			draw.text((245, 22), str(ctx.author), DARK, font=font_normal)
			draw.text((280, 98), f"Rank #{pos}", DARK, font=font_small)
			draw.text((280, 123), f"Level {level}", DARK, font=font_small)
			draw.text((280, 150), f"Exp {get_str(xp)}/{get_str((level+1)**5)}", DARK, font=font_small)
      
      
             # Adding another blank layer for the progress bar
             # Because drawing on card dont make their background transparent
			blank = Image.new("RGBA",card.size,(255,255,255,0))
			blank_draw = ImageDraw.Draw(blank)
			blank_draw.rectangle((245,185,750,205), fill=(255,255,255,0), outline=DARK) # Will be continued in section A-1
      
            # Simple calculation for the length of progress bar
			clxp = level ** 5
			nlxp = (level+1)**5 # Next level xp
			xpneed = nlxp - clxp
			xphave = xp - clxp
      
			cp   = (xphave/xpneed)*100 # Current percentage of gained xp
			lob= (cp * 4.9)+248 # Length of bar should be with offset of 248	
      
           # Section A-1
			blank_draw.rectangle((248,188,lob,202), fill=DARK)
			blank_draw.ellipse((20,20,218,218),fill=(255,255,255,0), outline=DARK)
			draw.text((810,195), "Ignite",DARK, font=font_signa)
        
            # Paste user profile picture in profile picture holder See section "A-2"
			profile_pic_holder.paste(npro, (29,29,209,209))
  
			out = Image.composite(profile_pic_holder,card,mask)
			out = Image.alpha_composite(out, blank)
      
            # Status badge
            # Another blank
			blank = Image.new("RGBA",out.size,(255,255,255,0))
			blank.paste(status, (173,173))
			blank.paste(leveli, (248,127))
			blank.paste(ranki, (245,95))
			blank.paste(xpi, (247, 151))
			
			out = Image.alpha_composite(out, blank)
       
           # Saving and sending
			ncn = f"static/img/{str(ctx.author.id)}{str(random.randint(1,100000))}.png"
			
			out.save(ncn)
			file = discord.File(fp=ncn, filename="card.png")
			await ctx.send(file=file)
    
            # Removing files to save space
			os.remove(ncn)
		else:
			await ctx.send("You are not ranked yet! Send some messages.")
  
        
def setup(client):
	client.add_cog(User(client))
