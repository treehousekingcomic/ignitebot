import discord
from discord.ext import commands
import asyncpg

class Invites(commands.Cog):
  """Check invites of a member."""
  def __init__(self, client):
    self.client = client
  
  async def ucmd(self, cmd:str):
  	data = await self.client.pgdb.fetchrow("SELECT * FROM cmduse WHERE name = $1", cmd)
  	
  	if data:
  		uses = data['uses'] + 1
  		await self.client.pgdb.execute("UPDATE cmduse SET uses = $1 WHERE name = $2", uses, data['name'])
  	else:
  		await self.client.pgdb.execute("INSERT INTO cmduse(name, uses) VALUES($1, $2)", cmd, 1)
  
  @commands.command(aliases=["ci"])
  async def checkinvites(self, ctx, user:discord.Member):
    """Check invites of a member"""
    await self.ucmd("checkinvites")
    invites = await ctx.guild.invites()
    #await ctx.send(invites)
    uinv = []
    for invite in invites:
      if invite.inviter == user:
        uinv.append(invite)
    count = 0
    for i in uinv:
      count += i.uses
    
    await ctx.send(f"**{user}** have {count} active invites in this server!")
    
def setup(client):
  client.add_cog(Invites(client))
  