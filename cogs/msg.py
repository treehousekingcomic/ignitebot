import discord
from discord.ext import commands
from discord.utils import get
import time
import typing
import asyncpg

class Announce(commands.Cog, name="Message"):
    """Send an user a message. Or send message in a channel. Only server administrators can send message. And when a message sent to a member, sender name and server name will be added"""
    def __init__(self, client):
        self.client = client
    
    async def ucmd(self, cmd:str):
      data = await self.client.pgdb.fetchrow("SELECT * FROM cmduse WHERE name = $1", cmd)
  	
      if data:
  	    uses = data['uses'] + 1
  	    await self.client.pgdb.execute("UPDATE cmduse SET uses = $1 WHERE name = $2", uses, data['name'])
      else:
          await self.client.pgdb.execute("INSERT INTO cmduse(name, uses) VALUES($1, $2)", cmd, 1)
    
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def msg(self, ctx, cu:typing.Union[discord.Member, discord.TextChannel, str], *, msg:str):
        """Send message to a user or member"""
        await self.ucmd("msg")
        try:
            if type(cu) == discord.Role:
              await ctx.send("Cant send msg to a role!")
            if type(cu) == discord.TextChannel:
                try:
                    await cu.send(msg)
                    await ctx.send("Message sent.")
                except:
                    await ctx.send("Cant send message there! Give me premissions")
            if type(cu) == discord.Member:
                try:
                    user = cu.mention
                    guild = "**" + ctx.guild.name + "**"
                    msg = msg.replace('{user}', user)
                    msg = msg.replace('{server}', guild)
                    msg = msg.replace('{server.members}', str(ctx.guild.member_count))
                    await cu.send(msg + f"\nSent by **{ctx.author}** From **{ctx.guild.name}**")
                    await ctx.send(f"Message sent to - **{user}**")
                except:
                    await ctx.send("I cant send message to the user!")
        except:
            await ctx.send("Something went wrong!")
    
def setup(client):
    client.add_cog(Announce(client))
