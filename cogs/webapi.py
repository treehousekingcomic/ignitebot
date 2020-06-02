import discord
from discord.ext import commands
import aiohttp
import asyncio
import os
import math
import typing
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
from colorthief import ColorThief
import dotenv

env_path = os.path.join(os.getcwd(), '.env')
dotenv.load_dotenv(dotenv_path=env_path)

GIPHYKEY=os.getenv("GIPHYKEY")
PIXABAYKEY=os.getenv("PIXABAYKEY")

class Api(commands.Cog):
  """Some use of cool APIs"""
  def __init__(self, client):
    self.client = client
  
  @commands.command()
  async def randommath(self, ctx):
    
    async with aiohttp.ClientSession() as s:
      async with s.get("http://numbersapi.com/random/math") as r:
        data = await r.text()
    
    await ctx.send(data)
  
  @commands.command()
  @commands.cooldown(1,30, commands.BucketType.user)
  async def pixabay(self, ctx,*,query):
    """Search images on pixabay"""
    
    sg = self.client.get_guild(700374484955299900)
    
    cou = 200
    
    nextbtn = discord.utils.get(sg.emojis, name="ignext")
    prevbtn = discord.utils.get(sg.emojis, name="igprev")
    skipf = discord.utils.get(sg.emojis, name="igskipf")
    skipb = discord.utils.get(sg.emojis, name="igskipb")
    beg = discord.utils.get(sg.emojis, name="igbeg")
    end = discord.utils.get(sg.emojis, name="igend")
    
    next = True
    query = query.replace(" ", "+")
    if cou < 3:
      cou = 3
    if cou > 200:
      cou = 200
    if ctx.channel.nsfw:
      ss = "&safesearch=false"
      se = "Disabled"
    else:
      ss = "&safesearch=true"
      se = "Enabled"
    try:
      async with aiohttp.ClientSession() as s:
        async with s.get(f"https://pixabay.com/api/?key={PIXABAYKEY}&q={query}&image_type=photo&pretty=true&per_page={cou}{ss}") as r:
          data = await r.json()
    except:
      await ctx.send("Something went wrong!")
      next = False
      
    count = 0
    fnd = 0
    while next:
      if len(data["hits"]) >0:
        try:
          r = data["hits"][count]
          fnd = len(data["hits"])
          #await ctx.send(r["largeImageURL"])
          embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
          embed.set_image(url=r["largeImageURL"])
          embed.add_field(name="Tags", value=r["tags"])
          embed.set_footer(text=f"Page {count+1}/{fnd} - Safesearch : {se}")
        except:
          await ctx.send("No more images found!")
          break
      else:
        await ctx.send("Nothing match your query!")
        break
      if count <=0:
        try:
          await msg.edit(embed=embed)
        except:
          msg = await ctx.send(embed=embed)
      else:
        await msg.edit(embed=embed)
        
      if count >0:
        await msg.add_reaction(beg)
        await asyncio.sleep(0.1)
        if count >4:
          await msg.add_reaction(skipb)
          await asyncio.sleep(0.1)
        await msg.add_reaction(prevbtn)
        await asyncio.sleep(0.1)
      if count < fnd -1:
        await msg.add_reaction(nextbtn)
        await asyncio.sleep(0.1)
        
      if fnd > 5 and count < fnd -1:
        await msg.add_reaction(skipf)
        await asyncio.sleep(0.1)
      if count < fnd -1:
        await msg.add_reaction(end)
        await asyncio.sleep(0.1)
        
      def check(r,u):
        return (u.id == ctx.author.id) and (r.message.id == msg.id)
      try:
        r, u = await self.client.wait_for("reaction_add", timeout=60, check=check)
      
        if r.emoji == nextbtn:
          count += 1
        elif r.emoji == prevbtn:
          count -= 1
        elif r.emoji == end:
          count = fnd-1
        elif r.emoji == beg:
          count = 0
        elif r.emoji == skipf:
          if count +5 > fnd-1:
            count = fnd -1
          else:
            count += 5
        elif r.emoji == skipb:
          if count -5 <0:
            count = 0
          else:
            count -= 5
        try:
          await msg.clear_reactions()
        except:
          pass
      except:
        try:
          await msg.clear_reactions()
        except:
          pass
        break
  
  
  @commands.command()
  @commands.cooldown(1,30, commands.BucketType.user)
  async def giphy(self, ctx,*, search:str="random"):
    """Search for gifs on giphy."""
    
    sg = self.client.get_guild(700374484955299900)
    
    nextbtn = discord.utils.get(sg.emojis, name="ignext")
    prevbtn = discord.utils.get(sg.emojis, name="igprev")
    skipf = discord.utils.get(sg.emojis, name="igskipf")
    skipb = discord.utils.get(sg.emojis, name="igskipb")
    beg = discord.utils.get(sg.emojis, name="igbeg")
    end = discord.utils.get(sg.emojis, name="igend")
    
    
    try:
      url = ""
      if search == "random":
        url = f"https://api.giphy.com/v1/gifs/random?api_key={GIPHYKEY}&rating=G"
      else:
        url = f"https://api.giphy.com/v1/gifs/search?api_key=GDCrrFk8RzjzjU0bwKQpfJNaY3Ypmb3M&q={search}&limit=30&offset=0&rating=G&lang=en"
      async with aiohttp.ClientSession() as s:
        async with s.get(str(url)) as r:
          data = await r.json()
          next = True
    except:
      await ctx.send("Nothing found!")
      next = False
      
    count = 0
    fnd = 0
    while next:
      if len(data["data"]) >0:
        try:
          if search == "random":
            r = data["data"]
            fnd = 1
          else:
            r = data["data"][count]
            fnd = len(data["data"])
          #await ctx.send(r["largeImageURL"])
          embed = discord.Embed(color=ctx.author.color, timestamp=ctx.message.created_at)
          embed.set_image(url=r["images"]["downsized_large"]["url"])
          embed.add_field(name="Title", value=r["title"] + "✔")
          embed.set_footer(text=f"Page {count+1}/{fnd}")
        except:
          await ctx.send("No more images found!")
          break
      else:
        await ctx.send("Nothing match your query!")
        break
      if count <=0:
        try:
          await msg.edit(embed=embed)
        except:
          msg = await ctx.send(embed=embed)
      else:
        await msg.edit(embed=embed)
        
      if count >0:
        await msg.add_reaction(beg)
        await asyncio.sleep(0.1)
        if count >4:
          await msg.add_reaction(skipb)
          await asyncio.sleep(0.1)
        await msg.add_reaction(prevbtn)
        await asyncio.sleep(0.1)
      if count < fnd -1:
        await msg.add_reaction(nextbtn)
        await asyncio.sleep(0.1)
        
      if fnd > 5 and count < fnd -1:
        await msg.add_reaction(skipf)
        await asyncio.sleep(0.1)
      if count < fnd -1:
        await msg.add_reaction(end)
        await asyncio.sleep(0.1)
        
      def check(r,u):
        return (u.id == ctx.author.id) and (r.message.id == msg.id)
      try:
        r, u = await self.client.wait_for("reaction_add", timeout=60, check=check)
      
        if r.emoji == nextbtn:
          count += 1
        elif r.emoji == prevbtn:
          count -= 1
        elif r.emoji == end:
          count = fnd-1
        elif r.emoji == beg:
          count = 0
        elif r.emoji == skipf:
          if count +5 > fnd-1:
            count = fnd -1
          else:
            count += 5
        elif r.emoji == skipb:
          if count -5 <0:
            count = 0
          else:
            count -= 5
        try:
          await msg.clear_reactions()
        except:
          pass
      except:
        try:
          await msg.clear_reactions()
        except:
          pass
        break
        
  @commands.command()
  async def short(self, ctx, *, link:str="hh"):
    """Shorten a link."""
    
    async with ctx.channel.typing():
      async with aiohttp.ClientSession() as s:
        async with s.get(f"https://api.shrtco.de/v2/shorten?url={link}") as r:
          data = await r.json()
    
      if data["ok"]:
        lnk = data["result"]["full_short_link"]
        ori = data["result"]["original_link"]
        embed = discord.Embed(color=ctx.author.color, description=f"Shorten link : {lnk} \nOriginal link : [here]({ori})", title="Url Shortner")
        await ctx.send(embed=embed)
      elif data["error_code"] == 10:
        await ctx.send("Cant short! Disallowed url.")
      elif data["error_code"] == 2:
        await ctx.send("Invalid url!")
  
  @commands.command()
  @commands.cooldown(1,5, commands.BucketType.user)
  async def kpop(self, ctx, *, name:str = None):
  	"""Get info of a KPOP member."""
  	
  	if name is None:
  		link = "https://apis.duncte123.me/kpop"
  	else:
  		link = f"https://apis.duncte123.me/kpop/{name}"
  		
  	async with aiohttp.ClientSession() as s:
  		async with s.get(link) as r:
  			data = await r.json()
  		
  	if data["success"]:
  		embed = discord.Embed(color=ctx.author.color, description=f"Name : {data['data']['name']} \nBand : {data['data']['band']}", title="Kpop")
  		embed.set_thumbnail(url=data['data']['img'])
  		await ctx.send(embed=embed)
  	else:
  		await ctx.send("No data found!")
 
def setup(client):
  client.add_cog(Api(client))