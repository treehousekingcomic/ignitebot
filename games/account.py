import discord
from discord.ext import commands
import time
import sqlite3
import random
import asyncpg

class Account(commands.Cog):
  """Manage your Game account"""
  def __init__(self, client):
    self.client = client
  
  async def ucmd(self, cmd:str):
  	data = await self.client.pgdb.fetchrow("SELECT * FROM cmduse WHERE name = $1", cmd)
  	
  	if data:
  		uses = data['uses'] + 1
  		await self.client.pgdb.execute("UPDATE cmduse SET uses = $1 WHERE name = $2", uses, data['name'])
  	else:
  		await self.client.pgdb.execute("INSERT INTO cmduse(name, uses) VALUES($1, $2)", cmd, 1)
  
  async def check_user(self, id):
    res = await self.client.pgdb.fetchrow(f"SELECT * FROM cash WHERE userid = $1", id)
    if res:
      pass
      #print("User already")
    else:
      await self.client.pgdb.execute(f"INSERT INTO cash(userid, cash) VALUES($1, 500)", id)
      #print("User added")
  
  async def get_cash(self, id):
    res = await self.client.pgdb.fetchrow(f"SELECT cash FROM cash WHERE userid =$1", id)
    return res['cash']
  
  async def update_cash(self, id, cash):
    cash = await self.get_cash(id)+ cash
    await self.client.pgdb.execute(f"UPDATE cash SET cash = $1 WHERE userid = $2", cash, id)
  
  @commands.command()
  @commands.cooldown(10, 60, commands.BucketType.user)
  async def cash(self, ctx):
    """Check your cash"""
    await self.ucmd("cash")
    #print(ctx)
    await self.check_user(ctx.author.id)
    print("x")
    cash = await self.get_cash(ctx.author.id)
    
    await ctx.send(f"**{ctx.author.name}** you have __**{str(cash)}**__ icash!")
  
  @commands.command()
  @commands.cooldown(1, 300, commands.BucketType.user)
  async def beg(self, ctx):
    """Beg for some cash every 5 minutes"""
    await self.ucmd("beg")
    await self.check_user(ctx.author.id)
    #possibilities = [100,10,50,22,40,19,68,67,500]
    reward = random.randint(100,500)
    gp = ['yes','no', 'yes', 'no', 'yes']
    g = random.choice(gp)
    
    if g == 'yes':
      await self.update_cash(ctx.author.id, reward)
      await ctx.send(f"Here you go! You got {reward} icash from **__Shahriyar#9770__**!")
    else:
      await ctx.send("Not this time! Try again....")
    
  @commands.command()
  async def give(self, ctx, amount, user:discord.Member):
    """Give cash to your friend."""
    await self.ucmd("give")
    cash = await self.get_cash(ctx.author.id)
    try:
      amount = int(amount)
    except:
      amount = 1
    
    if type(user) == discord.Member:
      if cash < amount:
        await ctx.send(f"**{ctx.author.name}** you dont have {amount} icash to give!")
      elif amount <= 0:
        await ctx.send("Is that even possible!")
      else:
        await self.update_cash(ctx.author.id, -amount)
        await self.update_cash(user.id, amount)
        if user == ctx.author:
          bhy = ".But....why...?"
        else:
          bhy = ""
        await ctx.send(f"💸 | **{ctx.author.name}** sent **{amount}** icash to **{user}**. {bhy}")
        
    else:
      await ctx.send("Please mention a valid user!")
    
    
  
def setup(client):
  client.add_cog(Account(client))