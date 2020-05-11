import discord
import sys
import humanize
import os
from discord.ext import commands
import asyncpg

class Info(commands.Cog):
  """Get bot info"""
  def __init__(self, client):
    self.client = client
  
  async def ucmd(self, cmd:str):
  	data = await self.client.pgdb.fetchrow("SELECT * FROM cmduse WHERE name = $1", cmd)
  	
  	if data:
  		uses = data['uses'] + 1
  		await self.client.pgdb.execute("UPDATE cmduse SET uses = $1 WHERE name = $2", uses, data['name'])
  	else:
  		await self.client.pgdb.execute("INSERT INTO cmduse(name, uses) VALUES($1, $2)", cmd, 1)
  
  @commands.group()
  async def info(self, ctx):
    """Get bot info"""
    await self.ucmd("info")
    
    pyv = str(sys.version_info[0]) + "." + str(sys.version_info[1]) + "." + str(sys.version_info[2])
    lib = "discord.py"
    dpv = str(discord.__version__)
    owner = "Shahriyar#9770"
    cmds = len(self.client.commands)
    shards = len(self.client.shards)
    
    dirs = [os.getcwd() + "/cogs", os.getcwd() + "/admin", os.getcwd() + "/games"]
    #await ctx.send(cwd)
    
    af = []
    for dir in dirs:
      for root, dirs, files in os.walk(dir):
        for file in files:
          if file.endswith(".py"):
            af.append(os.path.join(root,file))
    
    line = 0
    for file in af:
      with open(file, 'r') as f:
        lines = f.readlines()
        line += len(lines)
    with open("main.py", 'r') as f:
    	lines = f.readlines()
    	line += len(lines)
    
    
    des = ""
    des += "**Owner** : " + owner + "\n"
    des += "**Lib** : " + lib + ", v"+ dpv + "\n"
    des += "**Shards** : " + str(shards) + "\n"
    des += "**Python** : " + pyv + "\n"
    #des += "**Total commands** : " + str(cmds) + "\n"
    des += "**Active since** : " + str(humanize.naturaldate(self.client.user.created_at)) + "\n"
    des += "**Guilds** : " + str(len(self.client.guilds)) + "\n"
    des += "**Users** : " + str(len(self.client.users)) +"\n"
    
    des += "**Started** : " + humanize.naturaltime(self.client.launch_time)
    des += f"\n\n*This bot has `{len(af)+1}` files containing `{line}` lines of code and `{str(cmds)}` commands!*"
    #des += "[![Discord Bots](https://top.gg/api/widget/696975708907503636.svg)](https://top.gg/bot/696975708907503636)"
    embed = discord.Embed(color=ctx.author.color, description=des, title=self.client.user.name, timestamp=ctx.message.created_at)
    embed.set_thumbnail(url=self.client.user.avatar_url)
    
    await ctx.send(embed=embed)
  
  @commands.command()
  async def invite(self, ctx):
    await self.ucmd("invite")
    link = "https://discordapp.com/oauth2/authorize?client_id=696975708907503636&permissions=8&scope=bot"
    embed = discord.Embed(color=ctx.author.color, title="Ignite Invite", description=f"[click here]({link})")
    embed.set_thumbnail(url=self.client.user.avatar_url)
    await ctx.send(embed=embed)
def setup(client):
  client.add_cog(Info(client))