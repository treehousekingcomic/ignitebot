import discord
from discord.ext import commands 
import difflib
import time
import aiohttp
import asyncio
import os
import qrcode
import random
import asyncpg

class Covid(commands.Cog):
  """Realtime covid-19 statistics"""
  def __init__(self, client):
    self.client = client
  
  async def ucmd(self, cmd:str):
  	data = await self.client.pgdb.fetchrow("SELECT * FROM cmduse WHERE name = $1", cmd)
  	
  	if data:
  		uses = data['uses'] + 1
  		await self.client.pgdb.execute("UPDATE cmduse SET uses = $1 WHERE name = $2", uses, data['name'])
  	else:
  		await self.client.pgdb.execute("INSERT INTO cmduse(name, uses) VALUES($1, $2)", cmd, 1)
  
  @commands.command(aliases=['corona','covid-19','covid19'])
  async def covid(self, ctx, *,country:str=None):
    """Get stats of a country or whole world"""
    await self.ucmd("covid")
    gld = self.client.get_guild(700374484955299900)
    emj = discord.utils.get(gld.emojis, name="igloading")
    dn = discord.utils.get(gld.emojis, name="igtickmark")
    nd = discord.utils.get(gld.emojis, name="igcrossmark")
    data = None
    data2 = None
    await ctx.message.add_reaction(emj)
    await asyncio.sleep(0.1)
    if country is None:
      async with aiohttp.ClientSession() as s:
        async with s.get("https://covid19apis.herokuapp.com/api/v1/total/report") as resp:
          data = await resp.json()
          #print(data)
      ttl = "🌏 World Statistics of Covid-19"
      msg = ""
      msg += "**Confirmed Cases** : " + str(data[0]['confirmed']) +"\n"
      msg += "**Recovered** : " + str(data[0]['recovered']) +"\n"
      msg += "**Deaths** : " + str(data[0]['deaths'])
      ftr = "Stay Home, Stay Safe"
      
      embed = discord.Embed(colour=ctx.author.color, description=msg, title=ttl, timestamp=ctx.message.created_at)
      embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
      embed.set_footer(text=ftr)
      
      try:
        await ctx.message.clear_reactions()
      except:
        pass
      await ctx.message.add_reaction(dn)
      await ctx.send(embed=embed)
    else:
      async with aiohttp.ClientSession() as s:
        async with s.get(f"https://covid19apis.herokuapp.com/api/v2/nation/{country}/") as resp:
          data = await resp.json()
          #print(data)	
      #data = requests.get(url=f"https://covid19apis.herokuapp.com/api/v2/nation/{country}/").json()
      countries = []
      if len(data) > 1:    
        for row in data:
          countries.append(row['country'])
        matches = difflib.get_close_matches(country.upper(), countries, 5, 0.4)
        print(matches)
        nc = f"⚠️ | Error! Not content found for **__{country.upper()}__**\nMaybe - \n"
        for n in matches:
          nc += "■ " + n.upper() + "\n"
        
        time.sleep(0.1)
        
        try:
          await ctx.message.clear_reactions()
        except:
          pass
        await ctx.message.add_reaction(nd)
        await ctx.send(content=nc)
      elif len(data) == 1: 
        async with aiohttp.ClientSession() as s:
          async with s.get(f"https://covid19apis.herokuapp.com/api/v2/nation/{country}/") as resp:
            data = await resp.json()
        
        async with aiohttp.ClientSession() as s:
          async with s.get(f"https://covid19apis.herokuapp.com/api/v2/daily/{country}/") as resp:
            data2 = await resp.json()
          
        msg = ""
        ttl = f"Statistics of __{country.title()}__ - Covid-19"
        msg += "**Confirmed Cases** : " + str(data[0]['confirmed']) + f" (+{data2[0]['confirmed']})\n"
        msg += "**Recovered** : " + str(data[0]['recovered']) + f" (+{data2[0]['recovered']})\n"
        msg += "**Deaths** : " + str(data[0]['deaths']) + f" (+{data2[0]['deaths']})"
        ftr = "Stay Home, Stay Safe"
        
        embed = discord.Embed(colour=ctx.author.color, description=msg, title=ttl, timestamp=ctx.message.created_at)
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        embed.set_footer(text=ftr)
        
        try:
          await ctx.message.clear_reactions()
          await ctx.message.add_reaction(dn)
        except:
          pass
        await ctx.send(embed=embed)
      else:
        await ctx.send(content="Nothing found!")
    
def setup(client):
  client.add_cog(Covid(client))