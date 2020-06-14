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
  
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def msg(self, ctx, channel_or_member:typing.Union[discord.Member, discord.TextChannel, discord.Role, str], *, msg:str):
            """Send message to a user or member"""
            
            if type( channel_or_member) == discord.Role:
              await ctx.send("Cant send msg to a role!")
              
            if type( channel_or_member) == discord.TextChannel:
                try:
                    await  channel_or_member.send(discord.utils.escape_mentions(msg))
                    
                    await ctx.send("Message sent.")
                except:
                    await ctx.send("Cant send message there! Give me premissions")
                    
            if type( channel_or_member) == discord.Member:
                try:
                    user =  channel_or_member.mention
                    guild = "**" + ctx.guild.name + "**"
                    msg = msg.replace('{user}', user)
                    msg = msg.replace('{server}', guild)
                    msg = msg.replace('{server.members}', str(ctx.guild.member_count))
                    
                    msg = discord.utils.escape_mentions(msg)
                    
                    await  channel_or_member.send(msg + f"\nSent by **{ctx.author}** From **{ctx.guild.name}**")
                    await ctx.send(f"Message sent to - **{user}**")
                except:
                    await ctx.send("I cant send message to the user!")
    
def setup(client):
    client.add_cog(Announce(client))
