import discord
from discord.ext import commands 
import asyncpg

class Game(commands.Cog):
  """Set bots activity"""
  def __init__(self, client):
    self.client = client
  
  @commands.command(aliases=['game'], hidden=True)
  @commands.is_owner()
  async def activity(self, ctx, ttype:str='',*, ggame:str =''):
    """Set bots activity"""
    lst = ['playing', 'watching', 'streaming','listening']
    
    if ctx.author.id == 696939596667158579:
      if ttype == 'streaming' and ggame != '':
        #await ctx.send("Init")
        await self.client.change_presence(activity=discord.Streaming(name=ggame, url="https://hesdsup.vip"))
        await ctx.send(f"I am now streaming {ggame} 🔴")
      
      if ttype == 'playing' and ggame != '':
        await self.client.change_presence(activity=discord.Game(name=ggame))
        await ctx.send(f"I am now playing {ggame} ⚽️")
      
      if ttype == 'watching' and ggame != '':
        await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=ggame))
        await ctx.send(f"I am now watching {ggame} 👀")
        
      if ttype == 'listening' and ggame != 'x':
        await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=ggame))
        await ctx.send(f"Listening {ggame}🎶")
      if ttype not in lst:
        await ctx.send("Only `playing`, `watching`, `listening`, `streaming` is supported. Bots cant have custom activity for now!")
        
    else:
      await ctx.send("🐸 Only bot owner and authorized users can set activity!")
  
def setup(client):
  client.add_cog(Game(client))