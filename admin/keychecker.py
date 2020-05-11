import discord
import sqlite3
from discord.ext import tasks, commands
from datetime import datetime, timedelta
import asyncpg


class KeyCheck(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.check_exp.start()
    
    async def doit(self):
    	print("Checking for expired keys")
    	res = await self.client.pgdb.fetch("SELECT * FROM keys")
    	#print(res)
    	for result in res:
    		#print(result)
    		todate = result['expire']
    		#print(expiry_date)
    		
    		today = datetime.today()
    		
    		
    		if today.date() >= todate:
    			#print("Broken key")
    			key = result['key']
    			await self.client.pgdb.fetchrow(f"DELETE FROM keys WHERE key=$1", key)
 
    			guild = self.client.get_guild(result['guildid'])
    			await guild.owner.send("Your key is expired and all your tags paused!")
    		else:
    			pass

    @tasks.loop(minutes=10)
    async def check_exp(self):
        await self.doit()
        
		
def setup(client):
    client.add_cog(KeyCheck(client))
