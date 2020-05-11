import discord
import json
import os
import time
from discord.ext import commands
import typing

class Clear(commands.Cog):
  """Clear messages or Nuke a channel"""
  def __init__(self, client):
    self.client = client
  
  async def ucmd(self, cmd:str):
  	data = await self.client.pgdb.fetchrow("SELECT * FROM cmduse WHERE name = $1", cmd)
  	
  	if data:
  		uses = data['uses'] + 1
  		await self.client.pgdb.execute("UPDATE cmduse SET uses = $1 WHERE name = $2", uses, data['name'])
  	else:
  		await self.client.pgdb.execute("INSERT INTO cmduse(name, uses) VALUES($1, $2)", cmd, 1)

  @commands.command(aliases=['clr','c'])
  async def clear(self, ctx, amount='1'):
    """Clears specific amount of messages from current channel"""
    await self.ucmd("clear")
    
    if ctx.author.permissions_in(ctx.channel).manage_messages:
      try:
        self.limit = int(amount)
        try:
          await ctx.channel.purge(limit=self.limit + 1)
        except:
          try:
            await ctx.send("❌ | I can delete messages! Give me permission first!")
          except:
            await ctx.author.send("Looks like i have no permissions! Even I cant send message there")
      except:
        await ctx.send('```Please enter number as amount```')
    else:
      await ctx.send('```You dont have permission to Manage Message in this channel```')
    
  @commands.command()
  @commands.cooldown(1,5, commands.BucketType.channel)
  async def nuke(self, ctx, channel:typing.Union[discord.TextChannel, discord.VoiceChannel, str] = None):
    """Delete all mesaages of a channel"""
    await self.ucmd("nuke")
  	
    if ctx.author.permissions_in(ctx.channel).manage_messages:
      gld = self.client.get_guild(700374484955299900)
      tickemoji = discord.utils.get(gld.emojis, name="igtickmark")
      crossmoji = discord.utils.get(gld.emojis, name="igcrossmark")
      #await ctx.message.delete()
      if channel is not None and type(channel) != str:
        channnel = channel.mention
      else: 
        channnel = ctx.channel.mention
      msg = await ctx.send(f"⚠️ | Are you sure? {channnel} will be nuked. And this action cant be undone")
              
      await msg.add_reaction(tickemoji)
      time.sleep(0.3)
      await msg.add_reaction(crossmoji)

      def check(r, u):
        return (u.id == ctx.author.id) and (r.message.id == msg.id)
              
      try:
        r, u = await self.client.wait_for('reaction_add',timeout=20,check=check)
                
        if r.emoji.name == 'igtickmark':
          try:
            if type(channel) == discord.TextChannel:
              newc = await channel.clone()
              await channel.delete()
              await newc.send("💥 | Channel nuked!")
              await ctx.message.delete()
              await msg.delete()
            elif type(channel) == discord.VoiceChannel:
              await ctx.send("🚫 | Voice channels cant be nuked!")
            else:
              newc = await ctx.channel.clone()
              await ctx.channel.delete()
              await newc.send("💥 | Channel nuked!")     
          except:
            await ctx.send("⚠️ | I am missing permissions!")
        else:
          await msg.delete()
      except:
        await ctx.send("🕝 | Timeout!")
    else:
      await ctx.send("❌ | You dont have permission to do this!")

def setup(client):
  client.add_cog(Clear(client))
