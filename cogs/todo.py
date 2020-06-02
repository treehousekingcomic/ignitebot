import discord
from discord.ext import commands
import typing
import asyncpg

class Todo(commands.Cog):
	"""What to do?"""
	def __init__(self, client):
		self.client = client
 
	@commands.group(invoke_without_command=True)
	async def todo(self, ctx):
		"""Add, view and clear todo"""

		query = await self.client.pgdb.fetch(f"SELECT * FROM todos WHERE userid = $1", ctx.author.id)
		msg = ""
		count = 0
		
		for todo in query:
			count += 1
			msg += str(count) + ". __" +todo['content'] + "__\n"
		
		if count <= 0:
			await ctx.send(f"{ctx.author.mention} You have no ToDo! Add some 🙂")
		else:
			embed = discord.Embed(colour=ctx.author.color, description=msg, timestamp=ctx.message.created_at)
			embed.set_author(name=ctx.author.name + "'s Todos", icon_url=ctx.author.avatar_url)
			await ctx.send(embed=embed)
	
	@todo.command()
	async def add(self, ctx, *, text:str):
		await self.client.pgdb.execute("INSERT INTO todos(userid, content) VALUES($1, $2)", ctx.author.id, text)
		await ctx.send(f"Todo added! `{text}`")

	@todo.command()
	async def delete(self, ctx, index:int):
		try:
			index = int(index)
		except:
			await ctx.send("Index must be a ingeter. You wote a string!\nTry - `todo delete 1`")
      
		res = await self.client.pgdb.fetch("SELECT * FROM todos WHERE userid = $1", ctx.author.id)
		todos = len(res)
		
		if todos > 0:
			if index > 0 and index <= todos:
				delete = res[index-1]
				id = delete['id']
				con = delete['content']
				await self.client.pgdb.execute(f"DELETE FROM todos WHERE id = $1", id)
				await ctx.send(f"ToDo Deleted! `{con}`")
			else:
				await ctx.send("Wrong index!")
		else:
			await ctx.send("You dont have any ToDo to delete!")
	
	@todo.command()
	async def clear(self, ctx):
		await self.client.pgdb.execute(f"DELETE FROM todos WHERE userid= {ctx.author.id}")
		await ctx.send("Your ToDos has been cleared!")
		
def setup(client):
  client.add_cog(Todo(client))