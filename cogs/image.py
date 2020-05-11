import discord
from discord.ext import commands
import aiohttp
import random
import os
import typing
import math
import asyncio
from PIL import Image, ImageChops, ImageFilter, ImageDraw, ImageFont
from colorthief import ColorThief


class ImageEdit(commands.Cog, name="Image"):
	"""Some cool image filters and funny edits."""
	def __init__(self, client):
		self.client = client
	
	async def ucmd(self, cmd:str):
		data = await self.client.pgdb.fetchrow("SELECT * FROM cmduse WHERE name = $1", cmd)
  	
		if data:
			uses = data['uses'] + 1
			await self.client.pgdb.execute("UPDATE cmduse SET uses = $1 WHERE name = $2", uses, data['name'])
		else:
			await self.client.pgdb.execute("INSERT INTO cmduse(name, uses) VALUES($1, $2)", cmd, 1)
	
	async def dl_img(self, link, filename):
		async with aiohttp.ClientSession() as s:
			async with s.get(link) as r:
				data = await r.read()
		
		with open(filename, 'wb') as f:
			f.write(data)
	
	async def grn(self, id):
		return f"static/filter/{id}{random.randint(1000,9999)}.png"
	
	@commands.command()
	@commands.cooldown(1,10, commands.BucketType.user)
	async def stars(self, ctx):
		"""Add a layer of stars on your photo"""
		await self.ucmd("stars")
		link = str(ctx.author.avatar_url)
		fp = await self.grn(ctx.author.id)
		
		await self.dl_img(link, fp)
		
		im1 = Image.open(fp)
		im2 = Image.open("static/profile/stars.png")
		im2 = im2.resize(im1.size)
		
		out = ImageChops.add(im1,im2,1,0)
		out.save(fp)
		file = discord.File(fp=fp, filename="stars.png")
		await ctx.send(file=file)
		os.remove(fp)
	
	@commands.command()
	@commands.cooldown(1, 15, commands.BucketType.user)
	async def lovers(self, ctx, p1:discord.Member=None, p2:discord.Member=None):
		"""Make a couple photo"""
		await self.ucmd("lovers")
		if p2 is None:
			if p1 is None:
				await ctx.send("Please mention atleast one person!")
			else:
				girl = str(p1.avatar_url)
				boy = str(ctx.author.avatar_url)
		else:
			boy = str(p1.avatar_url)
			girl = str(p2.avatar_url)
  	
		img1 = await self.grn(ctx.author.id)
		img2 = await self.grn(ctx.author.id)
		
		await self.dl_img(boy, img1)
		await self.dl_img(girl, img2)
		
		frame = Image.open("static/profile/love.png")
		frame = frame.convert("RGBA")
		
		pic = Image.open(img1)
		pic2 = Image.open(img2)
		
		pic = pic.convert("RGBA")
		pic2 = pic2.convert("RGBA")
		
		pic = pic.resize((325, 325))
		pic2 = pic2.resize((325,325))
  	
		ph = Image.new("RGBA", (340,340), (255,255,255,0))
		ph2 = Image.new("RGBA", (350,350), (255,255,255,0))
		blank = Image.new("RGBA", frame.size, (255,255,255,0))
  
		ph.paste(pic, (7,7))
		ph2.paste(pic2, (12,12))
		pic = ph.rotate(4)
		pic2 = ph2.rotate(8)
  	
		blank.paste(pic, (240, 330))
		blank.paste(pic2, (650,278))
		out = Image.alpha_composite(blank, frame)
		out.save(img1)
  	
		file = discord.File(fp=img1, filename="lovers.png")
		await ctx.send(file=file)
		os.remove(img1)
		os.remove(img2)
	
	@commands.command()
	@commands.cooldown(1,10, commands.BucketType.user)
	async def frame(self, ctx, mem:typing.Union[discord.Member, str]=None):
		"""Add your photo in a frame. Or mention someone for his photo."""
		await self.ucmd("frame")
		imn = f"static/filter/{ctx.author.id}{random.randint(1000,99999)}.png"
		if mem is None:
			link = str(ctx.author.avatar_url)
		else:
			if type(mem) == str:
				link = mem
			else:
				link = str(mem.avatar_url)
 
		async with aiohttp.ClientSession() as s:
			async with s.get(link) as r:
				data = await r.read()

		with open(imn, "wb") as f:
			f.write(data)
  	
		pic = Image.open(imn)
		pic = pic.convert("RGBA")
		frame = Image.open("static/profile/frame.png")
		frame = frame.convert("RGBA")
  	
		background = pic.resize((442,442))
		background = background.filter(ImageFilter.GaussianBlur(radius=3))
  	
		blank = Image.new("RGBA", frame.size, (255,255,255,0))
  	
		newpic = pic.resize((130,130))
		blank.paste(newpic, (265,155))
		out = Image.alpha_composite(blank, frame)
		out = Image.alpha_composite(background, out)
		out = out.resize((600,600))
		out.save(imn)
  	
		file = discord.File(fp=imn, filename="frame.png")
		await ctx.send(file=file)
  	
		os.remove(imn)
	
	@commands.command()
	@commands.cooldown(1,10, commands.BucketType.user)
	async def edit(self, ctx, *, actions:str=""):
		"""Edit photo. Available actions : `TV`, `TP`, `FH`, `FV`, `R45` you can use any number in place of 45.  """
		await self.ucmd("Edit")
		
		if len(ctx.message.attachments) == 0:
			link = str(ctx.author.avatar_url)
		else:
			link = str(ctx.message.attachments[0].url)
  	
		img = f"static/filter/{ctx.author.id}{random.randint(1000,9999)}.png"
  	
		async with aiohttp.ClientSession() as s:
			async with s.get(link) as r:
				data = await r.read()
		
		with open(img, 'wb') as f:
			f.write(data)
		
		pic = Image.open(img)
		pic = pic.convert("RGBA")
		
		valid = ["FV", "FH", "TV", "TP"]
		ac = actions.split(" ")
		do = []
		for a in ac:
			if a in valid:
				do.append(a)
			elif a.startswith("R"):
				try:
					float(a[1:])
					do.append(a)
				except:
					pass
		if len(do) > 5:
			do = do[0:5]
			limiting = "(Max 5 operation is allowed)"
		else:
			limiting = ""
		
		msg = f"Editing photo {limiting}\n"
		
		m = await ctx.send(msg)
		for a in do:
			if a == "FH":
				pic = pic.transpose(Image.FLIP_LEFT_RIGHT)
				msg += "FLIPPING Left To Right\n"
				asyncio.sleep(0.5)
				await m.edit(content= msg)
			if a == "FV":
				pic = pic.transpose(Image.FLIP_TOP_BOTTOM)
				msg += "FLIPPING Top To Bottom\n"
				asyncio.sleep(0.5)
				await m.edit(content= msg)
			if a == "TP":
				pic = pic.transpose(Image.TRANSPOSE)
				msg += "Transposing\n"
				asyncio.sleep(0.5)
				await m.edit(content= msg)
			if a == "TV":
				pic = pic.transpose(Image.TRANSVERSE)
				msg += "Transversing\n"
				asyncio.sleep(0.5)
				await m.edit(content= msg)
			if a.startswith("R"):
				amt = float(a[1:])
				pic = pic.rotate(amt, expand=True)
				asyncio.sleep(0.5)
				msg += f"ROTATING {amt} Degree\n"
				await m.edit(content= msg)
		
		blank = Image.new("RGBA", pic.size, (255,255,255,0))
		blank.paste(pic, (0,0))
  	
		blank.save(img)
		msg += "Done..."
		await m.edit(content=msg)
		file = discord.File(fp=img, filename="edit.png")
  	#await m.delete()
		await ctx.send(file=file)
		await m.delete()
		os.remove(img)
	
	@commands.command()
	@commands.cooldown(1,15, commands.BucketType.user)
	async def getcolors(self, ctx, mem:discord.Member=None):
		"""Get colors from a photo with color value"""
		await self.ucmd("getcolors")
		if mem is None:
			mem = ctx.author 
		link = str(mem.avatar_url)
		img = f"static/filter/{ctx.author.id}{random.randint(1000,9999)}.png"
  	
		async with aiohttp.ClientSession() as s:
			async with s.get(link) as r:
				data = await r.read()
		with open(img, 'wb') as f:
			f.write(data)
		
		colors = ColorThief.get_palette(ColorThief(img), color_count=5)
		im = Image.open(img)
		im= im.resize((500,500))
		im = im.convert("RGBA")
		
		blank = Image.new("RGBA", (100,500), (255,255,255,0))
		holder = Image.new("RGBA", (620, 500))
		draw = ImageDraw.Draw(blank)
		
		start = 0
		font = ImageFont.truetype("static/profile/font4.ttf", 15)
		for color in colors:
			draw.ellipse((0,start,100,start+100), fill=color)
			draw.text((20, start+40),'#%02x%02x%02x' % color , (255,255,255), font=font)
			start +=100
		
		holder.paste(im, (120,0))
		holder.paste(blank, (0, 0))
		
		holder.save(img)
		file = discord.File(img, "colors.png")
		await ctx.send(file=file)
		os.remove(img)

def setup(client):
	client.add_cog(ImageEdit(client))