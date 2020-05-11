import discord
from discord.ext import commands
from discord.utils import get
import asyncpg

class Moderation(commands.Cog):
    """Server moderation. Such as Kick, Ban, Mute."""
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
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member:discord.Member, * , reason='Unspecified'):
        """Kicks someone. Requires kick members permission."""
        await self.ucmd("kick")
        try:
            await member.kick(reason=reason)
            await ctx.send(f'**{member.name}** has been kicked.')
        except:
        	await ctx.send(f"I dont have permissions to kick {member.name}")
    
    
    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member:discord.Member, * , reason='Unspecified'):
        """Bans someone. Requires ban members permission"""
        await self.ucmd("ban")
        try:
        	await member.ban(reason=reason)
        	await ctx.send(f'**{member.name} has been Banned**')
        except:
        	await ctx.send(f"I dont have permissions to kick {member.name}")
    
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member:discord.Member = None, *, reason='Unspecified'):
        """Mute someone. Requires manage roles permission. Also setup warning role first in server config."""
        await self.ucmd("mute")
        #await self.client.pgdb.execute("INSERT INTO guilddata(guildid, prefix) VALUES(696962067332071454, '..')")
        res =await self.client.pgdb.fetchrow("SELECT * FROM guilddata WHERE guildid= $1", ctx.guild.id)
        wnr = res['wnr']
        if member != None:
            embed = discord.Embed(colour=ctx.author.color,description=f"{member.name} muted for {reason}")
            embed.set_author(name=f"{member.name}", icon_url=member.avatar_url)
            embed.set_thumbnail(url=member.avatar_url)
            role = get(ctx.guild.roles, id=wnr)
            if role is not None:
            	await member.add_roles(role)
            	await ctx.send(embed=embed)
            else:
            	await ctx.send("Please setup a warning role! See `help config`")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member:discord.Member = None):
        """Unmutes a muted member"""
        await self.ucmd("unmute")
        res =await self.client.pgdb.fetchrow("SELECT * FROM guilddata WHERE guildid= $1", ctx.guild.id)
        wnr = res['wnr']
        if member != None:
            embed = discord.Embed(colour=ctx.author.color,description=f"{member.name} Unmuted")
            embed.set_author(name=f"{member.name}", icon_url=member.avatar_url)
            embed.set_thumbnail(url=member.avatar_url)
            role = get(ctx.guild.roles, id=wnr)
            can = False
            for r in member.roles:
            	if r == role:
            		can = True
            		break
            if can:
            	try:
            		await member.remove_roles(role)
            		await ctx.send(embed=embed)
            	except:
            		pass
            else:
            	await ctx.send("Already unmuted")
            	
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member:discord.Member,  role:discord.Role):
        """Give someone a role."""
        await self.ucmd("addrole")
        already = False
        for mrole in member.roles:
            if role == mrole:
                already = True
                break
            else:
            	pass
        if already == False:
            try:
        	    await member.add_roles(role)
        	    embed = discord.Embed(colour=ctx.author.color)
        	    embed.set_author(name=f"{member.name}", icon_url=member.avatar_url)
        	    embed.add_field(name="__Role Added__",value=f"Member : {member.mention} \nRole : {role.mention}")
        	    embed.set_footer(text=f"Role updated by - {ctx.author.name}")
        	    await ctx.send(embed=embed)
            except:
        	    await ctx.send("⛔ Missing manage roles permission or this role is higher than my role")
        else:
        	await ctx.send(f"🐸 {member.name} already has the role!")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, member:discord.Member,  role:discord.Role):
        """Remove a role from someone"""
        await self.ucmd("removerole")
        already = False
        for mrole in member.roles:
            if role == mrole:
                already = True
                break
            else:
            	pass
        if already:
            try:
        	    await member.remove_roles(role)
        	    embed = discord.Embed(colour=ctx.author.color)
        	    embed.set_author(name=f"{member.name}", icon_url=member.avatar_url)
        	    embed.add_field(name="__Role Removed__",value=f"Member : {member.mention} \nRole : {role.mention}")
        	    embed.set_footer(text=f"Role updated by - {ctx.author.name}")
        	    await ctx.send(embed=embed)
            except:
        	    await ctx.send("⛔ Missing manage roles permission or this role is higher than me")
        else:
        	await ctx.send(f"🙄 Don't be silly! {member.name} doesn't have the role!")

def setup(client):
    client.add_cog(Moderation(client))
