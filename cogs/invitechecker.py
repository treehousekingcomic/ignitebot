import discord
from discord.ext import commands
import asyncpg

class Invites(commands.Cog):
  """Check invites of a member."""
  def __init__(self, client):
    self.client = client
  
  @commands.command(aliases=["ci"])
  async def checkinvites(self, ctx, user:discord.Member=None):
    """Check invites of a member"""
    if user is None:
    	user = ctx.author
    
    invites = await ctx.guild.invites()
    uinv = [] # Not needed
    uinv = [invite for invite in invites if invite.inviter == user] # Get list of invites | Then you for loop for count or:
    count = len([invite for invite in invites if invite.inviter == user]) # Does everything and gives you a number
    
    await ctx.send(f"**{user}** have {count} active invites in this server!")
    
def setup(client):
  client.add_cog(Invites(client))
  
