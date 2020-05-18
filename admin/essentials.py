import discord
import json
import os
from discord.ext import tasks, commands
import traceback
import asyncio
import traceback
import sys

class Essentials(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_member_join(self, ctx):
		
		wres = await self.client.pgdb.fetchrow("SELECT * FROM guilddata WHERE guildid = $1", ctx.guild.id)
		
		if wres:
			wlcmsg = wres['wlcmsg']
			
		try:
			wlcmsg = wlcmsg.replace('{user}', ctx.mention)
			wlcmsg = wlcmsg.replace('{server}', ctx.guild.name)
			wlcmsg = wlcmsg.replace('{server.members}', str(ctx.guild.member_count))
			#print(wlcmsg)
		except:
			pass
    
		try:
		#res = await self.client.pgdb.fetchrow(f"SELECT * FROM guilddata WHERE guildid= $1", ctx.guild.id)
			role = discord.utils.get(ctx.guild.roles, id=wres['wr'])
			#print(role)
			await ctx.add_roles(role)
		except:
			pass

		try:
			res = await self.client.pgdb.fetchrow(f"SELECT * FROM guilddata WHERE guildid=$1", ctx.guild.id)
			g = ctx.guild.get_channel(res['wci'])
            
			msg = f'**🎯 | {ctx.name}** joined this server.'
			await g.send(msg)
		except:
			pass
		try:
			if wlcmsg != 'Null':
				await ctx.send(wlcmsg)
		except:
			pass
		
	@commands.Cog.listener()
	async def on_member_remove(self, ctx):
		await self.client.pgdb.execute(f"DELETE FROM levels WHERE userid = $1 AND guildid = $2", ctx.id, ctx.guild.id)
		try:
			query = await self.client.pgdb.fetchrow("SELECT * FROM guilddata WHERE guildid= $1", ctx.guild.id)
			g = ctx.guild.get_channel(query['bci'])
			msg = f"🚀 | **{ctx.name}** left this server."
			try:
				await g.send(msg)
			except:
				pass
		except:
			pass
	
	@commands.Cog.listener()
	async def on_raw_message_delete(self, message):
		self.id = message.message_id
		
		await self.client.pgdb.execute("DELETE FROM rr WHERE messageid =  $1", self.id)

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		sg = self.client.get_guild(700374484955299900)
		chan = discord.utils.get(sg.text_channels, id=711777804412387369)
		
		if hasattr(ctx.command, "on_error"):
				return
				
		if isinstance(error, commands.BotMissingPermissions):
			await ctx.send("⛔ | I cant do this without permission!")
		elif isinstance(error, commands.BadArgument):
			await ctx.send('🚫 | Bad Argument. Try Again.')
		elif isinstance(error, commands.MissingPermissions):
			await ctx.send('🙄 | You dont have permission to do this.')
		elif isinstance(error, commands.NotOwner):
			pass
		elif isinstance(error, commands.CommandNotFound):
			return
		elif isinstance(error, commands.CommandOnCooldown):
			#print(error.cooldown)
			if hasattr(ctx.command, "on_error"):
				return
			tt = ""
			if error.retry_after < 60:
				tt = str(round(error.retry_after,2)) + " Seconds"
			if error.retry_after > 60 and error.retry_after < 3600:
				min = int(error.retry_after) // 60
				sec = int(error.retry_after) % 60
				tt = str(min) + " Minute " + str(sec) + " Seconds"
			
			msg = await ctx.send(f"🕝 | Cooldown! wait {tt}!")
			if error.retry_after > 60:
				await asyncio.sleep(5)
			else:
				await asyncio.sleep(error.retry_after)
			await msg.delete()
		else:
			pass


	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		sg = self.client.get_guild(700374484955299900)
		chan = discord.utils.get(sg.text_channels, id=703622522503168126)
		await chan.send(f"🎉 Server invite: **{guild.name}** > **{guild.member_count}**")
    
		try:
			sc = guild.system_channel
			await sc.send("🏍 Beep. Boop. look, I am here! To get started type `..help`")
		except:
			await guild.owner.send("🏍 Beep. Boop. Look I am in your server. Go to your server and type `..help` to get started")

		res = await self.client.pgdb.fetchrow("SELECT * FROM guilddata WHERE guildid= $1", guild.id)
		
		if not res:
			await self.client.pgdb.execute("INSERT INTO guilddata(guildid, prefix, wnr, wci, bci, wr, igr) VALUES($1,$2, $3, $4, $5, $6, $7)", guild.id, "..", 0,0,0,0,0)
		elif res:
			await self.client.pgdb.execute("UPDATE guilddata SET prefix='..', wnr = 0, wci =0, bci=0, wr=0, igr=0 WHERE guildid = $1", guild.id)
	
	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		sg = self.client.get_guild(700374484955299900)
		chan = discord.utils.get(sg.text_channels, id=703622522503168126)
		await chan.send(f"👋 Server leave : **{guild.name}** > **{guild.member_count}**")
    
	@commands.command(hidden=True)
	@commands.is_owner()
	async def load(self, ctx, extension, folder='cogs'):
			try:
				self.client.load_extension(f'{folder}.{extension}')
				await ctx.send(f"Extension {extension.title()} Loaded successfully")
			except Exception as e:
				exc_type, exc_value, exc_tb = sys.exc_info()
				exc_content = traceback.format_exception(exc_type, exc_value, exc_tb)
				await ctx.send(f"```{exc_content}```")

	@commands.command(hidden=True)
	@commands.is_owner()
	async def unload(self, ctx, extension:str, folder:str="cogs"):
			try:
				self.client.unload_extension(f'{folder}.{extension}')
				await ctx.send(f"Extension {extension.title()} Unloaded successfully")
			except Exception as e:
				exc_type, exc_value, exc_tb = sys.exc_info()
				exc_content = traceback.format_exception(exc_type, exc_value, exc_tb)
				await ctx.send(f"```{exc_content}```")
				
	@commands.command(hidden=True)
	@commands.is_owner()
	async def reload(self, ctx, extension, folder='cogs'):
			try:
				#self.client.unload_extension(f'cogs.{extension}')
				self.client.reload_extension(f"{folder}.{extension}")
				await ctx.send(f"Extension {extension.title()} Reloaded successfully")
			except Exception as e:
				exc_type, exc_value, exc_tb = sys.exc_info()
				exc_content = traceback.format_exception(exc_type, exc_value, exc_tb)
				await ctx.send(f"```{exc_content}```")
	
				
def setup(client):
	client.add_cog(Essentials(client))