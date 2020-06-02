import discord
import sqlite3
from discord.ext import commands
from random import  randint
import datetime
import asyncpg
import aiohttp

class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client
           	
    async def check_avail(self, key:str):
    	res = await self.client.pgdb.fetch("SELECT * FROM keys WHERE key=$1", key)

    	if len(res) == 1:
    		return True
    	else:
    		return False
    
    async def chek_used(self, key:str):
    	res = await self.client.pgdb.fetchrow(f"SELECT guildid FROM keys WHERE key='{key}' ")
    	if res['guildid'] == 0:
    		return False
    	else:
    		return True
    
    async def do_reg(self, key:str, guildid:int, delta=None ):
    	try:
    		try:
    			await self.client.pgdb.execute("DELETE FROM keys WHERE guildid = $1", guildid)
    		except:
    			pass
    		if delta:
    			res = await self.client.pgdb.fetchrow("SELECT * FROM keys WHERE key = $1", key)
    			valid_till = res['valid_till'] + delta
    			await self.client.pgdb.execute(f"UPDATE keys SET guildid= $1, valid_till = $2 WHERE key= $3", guildid, valid_till, key)
    		else:
    			await self.client.pgdb.execute(f"UPDATE keys SET guildid= $1 WHERE key= $2", guildid, key)
    		return True
    	except:
    		return False

    async def generate_key(self):
    	datas = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
    	key = ""
    	while len(key) < 12:
    		key += datas[randint(0,len(datas)-1)]
    	return key
    
    @commands.command(hidden=True)
    @commands.is_owner()
    async def generate(self, ctx, xtime:int = 30, dmy:str = "D"):
    		key = await self.generate_key()
    		todays_date = datetime.datetime.now()

    		if dmy == "D":
    			expire_date = todays_date + datetime.timedelta(days=xtime)
    			
    		if dmy == "M":
    			expire_date = todays_date + datetime.timedelta(days=xtime*30)
    		
    		if dmy == "Y":
    			expire_date = todays_date + datetime.timedelta(days=xtime * 365)
    			
    		if dmy == "m":
    			expire_date = todays_date + datetime.timedelta(minutes=xtime)
    			
    		if dmy == "h":
    			expire_date = todays_date + datetime.timedelta(hours=xtime)  
    		
    		await self.client.pgdb.execute("INSERT INTO keys(key, guildid, created_at, valid_till) VALUES($1, $2, $3, $4)" , key, 0, todays_date, expire_date)
    		
    		await ctx.send(f"Key Generated : `{key}` for {xtime}{dmy}")
    		await ctx.send(f"```{key}```")
    
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def register(self, ctx, key:str):
    	isavailable = await self.check_avail(key)
    	res = await self.client.pgdb.fetchrow("SELECT * FROM keys WHERE guildid = $1", ctx.guild.id)
    	
    	if isavailable:
    		isused = await self.chek_used(key)
    		if isused:
    			await ctx.send("Key is already in use")
    		else:
    			if res:
    				valid_till = res['valid_till']
    				delta = valid_till - datetime.datetime.now()
    			else:
    				delta = None
    			suc = await self.do_reg(key, ctx.guild.id, delta)
    			if suc:
    				if delta:
    					msg = "This server's premium membership extended 🎉"
    				else:
    					msg = "This sever is now premium  🎉"
    				await ctx.send(msg)
    			else:
    				await ctx.send("Something went wrong.")
    	else:
    		await ctx.send("Key is wrong")
    
    @commands.command(hidden=True)
    @commands.is_owner()
    async def uses(self, ctx):
    	data = await self.client.pgdb.fetchrow("SELECT * FROM cmduse WHERE name = $1", "total")
    	msg = ""
    	
    	if data:
    		await ctx.send(f"Total command ran `{data['uses']}` time.")
    	else:
    		await ctx.send("No data to show!")
    		
    @commands.command(hidden=True)
    @commands.is_owner()
    async def upload(self, ctx ,fname):
    	lnk = ctx.message.attachments[0].url
    	async with aiohttp.ClientSession() as s:
    		async with s.get(lnk) as r:
    			data = await r.read()
    	
    	try:
    		with open(fname,'wb') as f:
    			f.write(data)
    		await ctx.send(f"Uploaded `{fname}`")
    	except:
    		await ctx.send("Upload failed!")
    
    @commands.command(hidden=True)
    @commands.is_owner()
    async def download(self, ctx, fname:str):
    	seg = fname.split("/")
    	total = len(seg)
    	oname = seg[total-1]
    	
    	try:
    		file = discord.File(fp=fname, filename=oname)
    		await ctx.send(file=file)
    	except:
    		await ctx.send("File not found!")
    
    @commands.command(hidden=True)
    async def source(self, ctx):
    	link = "https://github.com/shahprog/ignitebot"
    	sg = self.client.get_guild(700374484955299900)
    	members = sg.members
    	
    	if ctx.author in members:
    		embed = discord.Embed(title="Source Code", description=f"This is my source code in case if you wonder how i made this bot. Not for just copy pasting, just for getting help.\n \n[Source Code here]({link})")
    		embed.set_thumbnail(url=self.client.user.avatar_url)
    		embed.set_footer(text="shahprog/ignite")
    		embed.set_thumbnail(url=self.client.user.avatar_url)
    		embed.set_author(name="shahprog", url="https://github.com/shahprog/", icon_url=sg.owner.avatar_url)
    		await ctx.send(embed=embed)
    	else:
    		embed = discord.Embed(title="Support", description=f"You are not in the support server. Join to support the bot and get access to source code. \n\n[Join](https://discord.gg/7SaE8v2)")
    		embed.set_thumbnail(url=self.client.user.avatar_url)
    		embed.set_footer(text="Ignite")
    		embed.set_thumbnail(url=self.client.user.avatar_url)
    		embed.set_author(name="Ignite", url="https://discord.gg/7SaE8v2", icon_url=self.client.user.avatar_url)
    		await ctx.send(embed=embed)
    
    @commands.group(invoke_without_command=True, hidden=True )
    @commands.is_owner()
    async def disable(self, ctx):
    	"""Disable command cog or group"""
    	await ctx.send(f"Do `{ctx.prefix}help disable` to get help on this command")
    
    @disable.command(hidden=True)
    async def command(self, ctx, command:str=None):
    	if command is None:
    		return await ctx.send("Please specify a command to disable")
    	
    	cmd = self.client.get_command(command)
    	if cmd is None:
    		return await ctx.send("Not found!")
    	
    	if isinstance(cmd, commands.Group):
    		for c in cmd.commands:
    			try:
    				c.enabled = False
    			except Exception as e:
    				return await ctx.send(e)
    			finally:
    				cmd.enabled = False
    		await ctx.send(f"All the subcommands of `{cmd.qualified_name}` is disabled now")
    		
    	if isinstance(cmd, commands.Command):
    		try:
    			cmd.enabled = False
    		except Exception as e:
    			return await ctx.send(e)
    		await ctx.send(f"Command `{cmd.qualified_name}` is disabled now")
    
    @disable.command(hidden=True)
    @commands.is_owner()
    async def cog(self, ctx, cog:str=None):
    	if cog is None:
    		return await ctx.send("Please specify a cog")
    	
    	cogg = self.client.cogs[cog]
    	
    	if cogg is None:
    		return await ctx.send("Not found")
    	
    	for command in cogg.get_commands():
    		if isinstance(command, commands.Group):
    			for cmd in command.commands:
    				try:
    					cmd.enabled = False
    				except Exception as e:
    					await ctx.send(e)
    				finally:
    					command.enabled = False
    		if isinstance(command, commands.Command):
    			try:
    				command.enabled = False
    			except Exception as e:
    				await ctx.send(e)
    			
    	await ctx.send(f"All the command and group of `{cogg.qualified_name}` is disabled now")
    
    @commands.group(invoke_without_command=True, hidden=True )
    @commands.is_owner()
    async def enable(self, ctx):
    	"""Disable command cog or group"""
    	await ctx.send(f"Do `{ctx.prefix}help enable` to get help on this command")
    
    @enable.command(hidden=True)
    async def cmd(self, ctx, command:str=None):
    	if command is None:
    		return await ctx.send("Please specify a command to enable")
    	
    	cmd = self.client.get_command(command)
    	if cmd is None:
    		return await ctx.send("Not found!")
    	
    	if isinstance(cmd, commands.Group):
    		for c in cmd.commands:
    			try:
    				c.enabled = False
    			except Exception as e:
    				return await ctx.send(e)
    			finally:
    				cmd.enabled = True
    		await ctx.send(f"All the subcommands of `{cmd.qualified_name}` is disabled now")
    		
    	if isinstance(cmd, commands.Command):
    		try:
    			cmd.enabled = True
    		except Exception as e:
    			return await ctx.send(e)
    		await ctx.send(f"Command `{cmd.qualified_name}` is disabled now")
    
    @enable.command(hidden=True)
    @commands.is_owner()
    async def cogg(self, ctx, cog:str=None):
    	if cog is None:
    		return await ctx.send("Please specify a cog")
    	
    	cogg = self.client.cogs[cog]
    	
    	if cogg is None:
    		return await ctx.send("Not found")
    	
    	for command in cogg.get_commands():
    		if isinstance(command, commands.Group):
    			for cmd in command.commands:
    				try:
    					cmd.enabled = True
    				except Exception as e:
    					await ctx.send(e)
    				finally:
    					command.enabled = True
    		if isinstance(command, commands.Command):
    			try:
    				command.enabled = True
    			except Exception as e:
    				await ctx.send(e)
    			
    	await ctx.send(f"All the command and group of `{cogg.qualified_name}` is enabled now")
    		
def setup(client):
    client.add_cog(Admin(client))