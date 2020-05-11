import discord
from discord.ext import tasks, commands

class Morse(commands.Cog):
	"""Morse code generate and read"""
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
	async def morsify(self, ctx, *,word:str=None):
		"""Generate morse code from a text"""
		await self.ucmd("morsify")
		code = {
			"a" : ".-",
			"b" : "-...",
			"c" : "-.-.",
			"d" : "-..",
			"e" : ".",
			"f" : "..-.",
			"g" : "--.",
			"h" : "....",
			"i"  : "..",
			"j"  : ".---",
			"k" : "-.-",
			"l"  : ".-..",
			"m" : "--",
			"n" : "-.",
			"o" : "---",
			"p" : ".--.",
			"q" : "--.-",
			"r"  : ".-.",
			"s" : "...",
			"t" : "-",
			"u": "..-",
			"v" : "...-",
			"w" : ".--",
			"x"  : "-..-",
			"y"  : "-.--",
			"z" : "--..",
			"1" : ".----",
			"2" : "..---",
			"3" : "...--",
			"4" : "....-",
			"5" : ".....",
			"6" : "-....",
			"7" : "--...",
			"8" : "---..",
			"9" : "----.",
			"0" : "-----",
		}
		word = str(word).lower().replace(".", "").replace("-", "")
		chars = list(word)
		msg = ""
		for w in chars:
			try:
				msg += code[w] + " "
			except:
				msg += " "
				
		if len(list(word)) > 500:
			await ctx.send("This string is too big for me to decode!")
		else:
			try:
				await ctx.send(msg)
			except:
				await ctx.send("Something went wrong!")
	
	@commands.command()
	async def demorse(self, ctx, *,word:str=None):
		"""Read morse code"""
		await self.ucmd("demorse")
		code = {
			".-" : "a",
			"-..." : "b",
			"-.-." : "c",
			"-.." : "d",
			"." : "e",
			"..-." : "f",
			"--.": "g",
			"...." : "h",
			".." : "i",
			".---" : "j",
			"-.-" : "k",
			".-.." : "l",
			"--" : "m",
			"-." : "n",
			"---" : "o",
			".--." : "p",
			"--.-" : "q",
			".-." : "r",
			"..." : "s",
			"-" : "t",
			"..-" : "u",
			"...-" : "v",
			".--" : "w",
			"-..-" : "x",
			"-.--" : "y",
			"--.." : "z",
			".----" : "1",
			"..---" : "2",
			"...--" : "3",
			"....-" : "4",
			"....." : "5",
			"-...." : "6",
			"--..." : "7",
			"---.." : "8",
			"----." : "9",
			"-----" : "0",
		}
		word = str(word).lower()
		chars = word.split(" ")
		msg = ""
		
		for w in chars:
			try:
				msg += code[w]
			except:
				msg += " "
			
		if len(list(word)) > 2000:
			await ctx.send("This string is too big for me to decode!")
		else:
			try:
				await ctx.send(msg)
			except:
				await ctx.send("Something went wrong!")
	
def setup(client):
	client.add_cog(Morse(client))