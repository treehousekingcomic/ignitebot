#pylint:disable=W0312
import discord
from discord.ext import commands
import traceback
import asyncio

class Essentials(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		sg = self.client.get_guild(700374484955299900)
		chan = discord.utils.get(sg.text_channels, id=711777804412387369)
		

		if isinstance(error, commands.BotMissingPermissions):
			if hasattr(ctx.command, "on_error"):
				return
			
			await ctx.send("I cant do this without permission!")
			
		elif isinstance(error, commands.BadArgument):
			if hasattr(ctx.command, "on_error"):
				return
			
			await ctx.send('Bad Argument. Try Again.')
			
		elif isinstance(error, commands.MissingPermissions):
			if hasattr(ctx.command, "on_error"):
				return
			
			await ctx.send('🙄 | You dont have permission to do this.')
		
		elif isinstance(error, commands.NotOwner):
			if hasattr(ctx.command, "on_error"):
				return
			pass
		
		elif isinstance(error, commands.CommandNotFound):
			return
		
		elif isinstance(error, commands.CommandOnCooldown):
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
		
		elif isinstance(error, commands.MissingRequiredArgument):
			if hasattr(ctx.command, "on_error"):
				return
			
			await ctx.send(f"`{error.param.name}` is missing")
	
				
def setup(client):
	client.add_cog(Essentials(client))
