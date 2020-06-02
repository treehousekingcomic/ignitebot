import discord
import json
import sqlite3
import os
import time
from discord.ext import commands
import asyncpg

class ReactionRole(commands.Cog, name="Reactrole"):
  """Enable reaction role feature."""
  def __init__(self, client):
    self.client = client
  
  @commands.Cog.listener()
  async def on_raw_reaction_add(self, r):
    try:
      self.id = r.message_id
      self.emid = r.emoji.id
      query = await self.client.pgdb.fetch('SELECT * FROM rr WHERE messageid = $1 AND emojiid = $2', self.id, self.emid)
    
      if r.member.id != self.client.user.id:
        for res in query:
          role = discord.utils.get(r.member.guild.roles, id=res['roleid'])
          try:
          	await r.member.add_roles(role)
          except:
          	pass
    except:
      pass
  
  @commands.Cog.listener()
  async def on_raw_reaction_remove(self, r):
    try:
      self.id = r.message_id
      result = await self.client.pgdb.fetchrow("SELECT * FROM rr WHERE messageid = $1 AND emojiid = $2", self.id, r.emoji.id)
    
      guild = self.client.get_guild(r.guild_id)
      user = guild.get_member(r.user_id)
    
      role = discord.utils.get(guild.roles, id=result['roleid'])
      await user.remove_roles(role)
    except:
      pass

  @commands.command(aliases=['arr', 'rr'])
  @commands.has_permissions(administrator=True)
  async def addreactrole(self, ctx, message_id:int, emoji, role:discord.Role=None):
    """Add reaction role to a message. Needs developer mode enabled in your account settings. To copy message id."""
    
    try:
      self.emoji_id = int(emoji.strip("<>").split(":")[2])
    except:
      self.emoji_id = 0
      await ctx.send("This emoji cant be used. Please upload emoji in your server emoji slot to to use for react role")
      role = None
    
    if role != None:
      if role.managed == False:
        try:
          msg = await ctx.channel.fetch_message(message_id)
          try:
            emoj = discord.utils.get(ctx.guild.emojis, name=emoji.strip("<>").split(":")[1])
            await msg.add_reaction(emoj)
            await self.client.pgdb.execute("INSERT INTO rr(messageid, roleid, emojiid, guildid) VALUES($1,$2,$3,$4)",message_id, role.id, self.emoji_id, ctx.guild.id)
            mssg = await ctx.send("React role added!")
            try:
              await mssg.delete(delay=2)
            except:
              pass
          except:
          	await ctx.send("Only server emoji is allowed!")
        except:
          await ctx.send("Could not find that message in this channel! Go to that cannel where the message is.")
      else:
        await ctx.send("This role is managed by other bot or webhook! Cant be assigned to others. Please use a different role")
    await ctx.message.delete(delay=2)
  
  
def setup(client):
    client.add_cog(ReactionRole(client))
