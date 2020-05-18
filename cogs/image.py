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
import functools


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
	
	def get_stars(self, fp):
		im1 = Image.open(fp)
		im2 = Image.open("static/profile/stars.png")
		im2 = im2.resize(im1.size)
		try:
			out = ImageChops.add(im1,im2,1,0)
			out.save(fp)
			return fp
		except:
			os.remove(fp)
			return Flase
	
	@commands.command()
	@commands.cooldown(1,10, commands.BucketType.user)
	async def stars(self, ctx):
		"""Add a layer of stars on your photo"""
		await self.ucmd("stars")
		link = str(ctx.author.avatar_url)
		fp = await self.grn(ctx.author.id)
		
		await self.dl_img(link, fp)
		
		# Running blocking stuff in a executor
		thing = functools.partial(self.get_stars, fp)
		some_stuff = await self.client.loop.run_in_executor(None, thing)
  	
		if some_stuff:
			file = discord.File(fp=some_stuff, filename="stars.png")
			await ctx.send(file=file)
			os.remove(fp)
		else:
			await ctx.send("Something went wrong with your image!")
	
	def get_lovers(self, img1, img2):
		
		frame = Image.open("static/profile/love.png")
		frame = frame.convert("RGBA")
		
		try:
			pic = Image.open(img1)
			pic2 = Image.open(img2)
		except:
			return False
		
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
		os.remove(img2)
		
		return img1
		
	
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
  	
		img1 = f"static/filter/{id}{random.randint(1000,9999)}.png"
		img2 = f"static/filter/{id}{random.randint(1000,9999)}.png"
		
		await self.dl_img(boy, img1)
		await self.dl_img(girl, img2)
		
		# Running blocking stuff in a executor
		thing = functools.partial(self.get_lovers, img1, img2)
		some_stuff = await self.client.loop.run_in_executor(None, thing)
  	
  	
		if some_stuff:
			file = discord.File(fp=some_stuff, filename="lovers.png")
			await ctx.send(file=file)
			os.remove(some_stuff)
		else:
			await ctx.send("Something went wrong with your images!")
	
	def get_frame(self, imn, data):
		with open(imn, "wb") as f:
			f.write(data)
  	
		try:
			pic = Image.open(imn)
		except:
			os.remove(imn)
			return False
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
		
		return imn
	
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
		
		# Running blocking stuff in a executor
		thing = functools.partial(self.get_frame, imn, data)
		some_stuff = await self.client.loop.run_in_executor(None, thing)
  	
		if some_stuff:
			file = discord.File(fp=some_stuff, filename="frame.png")
			await ctx.send(file=file)
  	
			os.remove(imn)
		else:
			await ctx.send("Something went wrong with your image!")
		
	
	def get_colors(self, img, data):
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
		return img
	
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
		
		thing = functools.partial(self.get_colors, img, data)
		some_stuff = await self.client.loop.run_in_executor(None, thing)
		
		file = discord.File(some_stuff , "colors.png")
		await ctx.send(file=file)
		os.remove(img)

def setup(client):
	client.add_cog(ImageEdit(client))