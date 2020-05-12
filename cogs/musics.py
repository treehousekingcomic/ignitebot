"""The MIT License (MIT)

Copyright (c) 2019-2020 PythonistaGuild

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

-------------------------------------------------------------------------------
This example uses the following whihch must be installed prior to running:

    - Discord.py version >= 1.3.1 (pip install -U discord.py)
    - Wavelink version >= 0.5.1 (pip install -U wavelink)
    - menus version >= 1.0.0-a (pip install -U git+https://github.com/Rapptz/discord-ext-menus.git)
    - Python 3.7+
--------------------------------------------------------------------------------
"""
import asyncio
import async_timeout
import copy
import datetime
import discord
import math
import random
import re
import typing
import wavelink
import asyncio
from discord.ext import commands, menus

# URL matching REGEX...
URL_REG = re.compile(r'https?://(?:www\.)?.+')


class NoChannelProvided(commands.CommandError):
    """Error raised when no suitable voice channel was supplied."""
    pass


class IncorrectChannelError(commands.CommandError):
    """Error raised when commands are issued outside of the players session channel."""
    pass


class Track(wavelink.Track):
    """Wavelink Track object with a requester attribute."""

    __slots__ = ('requester', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        self.requester = kwargs.get('requester')


class Player(wavelink.Player):
    """Custom wavelink Player class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.context: commands.Context = kwargs.get('context', None)
        if self.context:
            self.dj: discord.Member = self.context.author

        self.queue = asyncio.Queue()
        self.controller = None

        self.waiting = False
        self.updating = False

        self.pause_votes = set()
        self.resume_votes = set()
        self.skip_votes = set()
        self.shuffle_votes = set()
        self.stop_votes = set()

    async def do_next(self) -> None:
        if self.is_playing or self.waiting:
            return

        # Clear the votes for a new song...
        self.pause_votes.clear()
        self.resume_votes.clear()
        self.skip_votes.clear()
        self.shuffle_votes.clear()
        self.stop_votes.clear()

        try:
            self.waiting = True
            with async_timeout.timeout(300):
                track = await self.queue.get()
        except asyncio.TimeoutError:
            # No music has been played for 5 minutes, cleanup and disconnect...
            return await self.teardown()

        await self.play(track)
        self.waiting = False

        # Invoke our players controller...
        await self.invoke_controller()

    async def invoke_controller(self) -> None:
        """Method which updates or sends a new player controller."""
        if self.updating:
            return

        self.updating = True

        if not self.controller:
            self.controller = InteractiveController(embed=self.build_embed(), player=self)
            await self.controller.start(self.context)

        elif not await self.is_position_fresh():
            try:
                await self.controller.message.delete()
            except discord.HTTPException:
                pass

            self.controller.stop()

            self.controller = InteractiveController(embed=self.build_embed(), player=self)
            await self.controller.start(self.context)

        else:
            embed = self.build_embed()
            await self.controller.message.edit(content=None, embed=embed)

        self.updating = False

    def build_embed(self) -> typing.Optional[discord.Embed]:
        """Method which builds our players controller embed."""
        track = self.current
        if not track:
            return

        channel = self.bot.get_channel(int(self.channel_id))
        qsize = self.queue.qsize()

        embed = discord.Embed(title=f'Music', colour=0xebb145)
        embed.description = f'Now Playing:\n**`{track.title}`** [{str(datetime.timedelta(milliseconds=int(track.length)))}] \n\n'
        embed.set_thumbnail(url=track.thumb)

        #embed.add_field(name='Duration', value=str(datetime.timedelta(milliseconds=int(track.length))))
        #embed.add_field(name='Queue Length', value=str(qsize))
        embed.add_field(name='Volume', value=f'**`{self.volume}%`**')
        embed.add_field(name='Requested By', value=track.requester.mention)
        #embed.add_field(name='DJ', value=self.dj.mention)
        #embed.add_field(name='Video URL', value=f'[Click Here!]({track.uri})')
        embed.set_footer(text=f"Remaining {str(qsize)} songs")

        return embed

    async def is_position_fresh(self) -> bool:
        """Method which checks whether the player controller should be remade or updated."""
        try:
            async for message in self.context.channel.history(limit=5):
                if message.id == self.controller.message.id:
                    return True
        except (discord.HTTPException, AttributeError):
            return False

        return False

    async def teardown(self):
        """Clear internal states, remove player controller and disconnect."""
        try:
            await self.controller.message.delete()
        #except discord.HTTPException:
        except:
            pass

        try:
        	self.controller.stop()
        except:
        	pass

        try:
            await self.destroy()
        except KeyError:
            pass


class InteractiveController(menus.Menu):
    """The Players interactive controller menu class."""

    def __init__(self, *, embed: discord.Embed, player: Player):
        super().__init__(timeout=None)

        self.embed = embed
        self.player = player

    def update_context(self, payload: discord.RawReactionActionEvent):
        """Update our context with the user who reacted."""
        ctx = copy.copy(self.ctx)
        ctx.author = payload.member

        return ctx

    def reaction_check(self, payload: discord.RawReactionActionEvent):
        if payload.event_type == 'REACTION_REMOVE':
            return False

        if not payload.member:
            return False
        if payload.member.bot:
            return False
        if payload.message_id != self.message.id:
            return False
        if payload.member not in self.bot.get_channel(int(self.player.channel_id)).members:
            return False

        return payload.emoji in self.buttons

    async def send_initial_message(self, ctx: commands.Context, channel: discord.TextChannel) -> discord.Message:
        return await channel.send(embed=self.embed)

    @menus.button(emoji='\u25B6')
    async def resume_command(self, payload: discord.RawReactionActionEvent):
        """Resume button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('resume')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\u23F8')
    async def pause_command(self, payload: discord.RawReactionActionEvent):
        """Pause button"""
        ctx = self.update_context(payload)

        command = self.bot.get_command('pause')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\u23F9')
    async def stop_command(self, payload: discord.RawReactionActionEvent):
        """Stop button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('stop')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\u23ED')
    async def skip_command(self, payload: discord.RawReactionActionEvent):
        """Skip button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('skip')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\U0001F500')
    async def shuffle_command(self, payload: discord.RawReactionActionEvent):
        """Shuffle button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('shuffle')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\u2795')
    async def volup_command(self, payload: discord.RawReactionActionEvent):
        """Volume up button"""
        ctx = self.update_context(payload)

        command = self.bot.get_command('vol_up')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\u2796')
    async def voldown_command(self, payload: discord.RawReactionActionEvent):
        """Volume down button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('vol_down')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\U0001F1F6')
    async def queue_command(self, payload: discord.RawReactionActionEvent):
        """Player queue button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('queue')
        ctx.command = command

        await self.bot.invoke(ctx)


class PaginatorSource(menus.ListPageSource):
    """Player queue paginator class."""

    def __init__(self, entries, *, per_page=8):
        super().__init__(entries, per_page=per_page)

    async def format_page(self, menu: menus.Menu, page):
        embed = discord.Embed(title='Coming Up...', colour=0x4f0321)
        embed.description = '\n'.join(f'`{index}. {title}`' for index, title in enumerate(page, 1))

        return embed

    def is_paginating(self):
        # We always want to embed even on 1 page of results...
        return True


class Musics(commands.Cog, name="Music"):
    """Listen to musics. (On development, May not be stable)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        if not hasattr(bot, 'wavelink'):
            bot.wavelink = wavelink.Client(bot=bot)

        bot.loop.create_task(self.start_nodes())

    async def start_nodes(self) -> None:
        """Connect and intiate nodes."""
        await self.bot.wait_until_ready()

        if self.bot.wavelink.nodes:
            previous = self.bot.wavelink.nodes.copy()

            for node in previous.values():
                await node.destroy()

        nodes = {'MAIN': {'host': '0.0.0.0',
                          'port': 8080,
                          'rest_uri': 'http://0.0.0.0:8080',
                          'password': 'testing',
                          'identifier': 'MAIN',
                          'region': 'us_central'
                          }}

        for n in nodes.values():
            node = await self.bot.wavelink.initiate_node(**n)
            node.set_hook(self.node_event_hook)

    async def node_event_hook(self, event: wavelink.WavelinkEvent) -> None:
        """Node event hook."""
        if isinstance(event, (wavelink.TrackStuck, wavelink.TrackException, wavelink.TrackEnd)):
            await event.player.do_next()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.bot:
            return

        player: Player = self.bot.wavelink.get_player(member.guild.id, cls=Player)

        if not player.channel_id or not player.context:
            player.node.players.pop(member.guild.id)
            return

        channel = self.bot.get_channel(int(player.channel_id))

        if member == player.dj and after.channel is None:
            for m in channel.members:
                if m.bot:
                    continue
                else:
                    player.dj = m
                    return

        elif after.channel == channel and player.dj not in channel.members:
            player.dj = member

    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        """Cog wide error handler."""
        if isinstance(error, IncorrectChannelError):
            return

        if isinstance(error, NoChannelProvided):
            return await ctx.send('You must be in a voice channel or provide one to connect to.')

    async def cog_check(self, ctx: commands.Context):
        """Cog wide check, which disallows commands in DMs."""
        if not ctx.guild:
            await ctx.send('Music commands are not available in Private Messages.')
            return False

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        """Coroutine called before command invocation.

        We mainly just want to check whether the user is in the players controller channel.
        """
        player: Player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player, context=ctx)

        if player.context:
            if player.context.channel != ctx.channel:
                await ctx.send(f'{ctx.author.mention}, you must be in {player.context.channel.mention} for this session.')
                raise IncorrectChannelError

        if ctx.command.name == 'connect' and not player.context:
            return
        #elif self.is_privileged(ctx):
#            return

        if not player.channel_id:
            return

        channel = self.bot.get_channel(int(player.channel_id))
        if not channel:
            return

        if player.is_connected:
            if ctx.author not in channel.members:
                await ctx.send(f'{ctx.author.mention}, you must be in `{channel.name}` to use voice commands.')
                raise IncorrectChannelError

    def required(self, ctx: commands.Context):
        """Method which returns required votes based on amount of members in a channel."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)
        channel = self.bot.get_channel(int(player.channel_id))
        required = math.ceil((len(channel.members) - 1) / 2.5)

        if ctx.command.name == 'stop':
            if len(channel.members) - 1 == 2:
                required = 2

        return required
        
    @commands.command(aliases=["join"])
    async def connect(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        """Connect to a voice channel."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if player.is_connected:
            return

        channel = getattr(ctx.author.voice, 'channel', channel)
        if channel is None:
            return await ctx.send("You must be in a voice channel first.")
        else:
            await player.connect(channel.id)
            await ctx.send(f"Connected to `{channel.name}` and binded to `{ctx.channel.name}`")

    @commands.command()
    async def play(self, ctx: commands.Context, *, query: str=None):
        """Play or queue a song with the given query."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            await ctx.invoke(self.connect)
            await asyncio.sleep(1)
        
        if player.is_paused and query is None:
            try:
                return await player.set_pause(False)
            except:
                return
        elif not player.is_paused and query is None:
        	pass
        	#return await ctx.send("Please enter a song name to play!")
            	
        if player.is_connected and query is not None:
            await ctx.send(f"🔍 Searching for `{query}`")
            query = query.strip('<>')
            if not URL_REG.match(query):
                query = f'ytsearch:{query}'

            tracks = await self.bot.wavelink.get_tracks(query)
            if not tracks:
                return await ctx.send('🚫 No songs were found with that query. Please try again.', delete_after=15)

            if isinstance(tracks, wavelink.TrackPlaylist):
                for track in tracks.tracks:
                    track = Track(track.id, track.info, requester=ctx.author)
                    await player.queue.put(track)

                await ctx.send(f'🎶 Playing {tracks.data["playlistInfo"]["name"]}'
                           f' with {len(tracks.tracks)} songs to the queue.\n')
            else:
                track = Track(tracks[0].id, tracks[0].info, requester=ctx.author)
                await ctx.send(f'\n🎧 Added {track.title} to the Queue\n', delete_after=15)
                await player.queue.put(track)

            if not player.is_playing:
                await player.do_next()
    
    @commands.command()
    @commands.check_any(commands.has_any_role("DJ", "Dj", "dj"), commands.has_permissions(administrator=True), commands.is_owner())
    async def pause(self, ctx: commands.Context):
        """Pause the currently playing song."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if player.is_paused or not player.is_connected:
            return

        try:
            await ctx.send('▶ Player paused.', delete_after=10)
            player.pause_votes.clear()

            return await player.set_pause(True)
        except:
        	return
    
    @commands.command()
    @commands.check_any(commands.has_any_role("DJ", "Dj", "dj"), commands.has_permissions(administrator=True), commands.is_owner())
    async def seek(self, ctx: commands.Context, duration:int):
        """Seek the currently playing song."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if player.is_paused or not player.is_connected:
            return
        
        track = player.current
        length = track.length
        cp = player.position
        if (cp + (duration * 1000)) > length:
        	await ctx.send(f"This song is not that long to seek {duration} seconds. If you want to skip this song use the `skip` command.")
        	return
        elif (cp + (duration * 1000)) <0:
        	await ctx.send("Cant seek {duration} seconds.")
        	return
        else:
        	pass
        try:
        	await player.seek(player.position + (duration * 1000))
        	await ctx.send(f"Song seeked {duration} seconds. If you want to start from begining use `restart` command.")
        except:
        	return

    @seek.error
    async def on_error(self, ctx, error):
    	if isinstance(error, commands.MissingAnyRole):
    		await ctx.send("You must have the `DJ` role to seek the player.")
    	if isinstance(error, commands.MissingPermissions):
    		await ctx.send("You must have the `DJ` role to seek the player.")
    
    @commands.command()
    @commands.check_any(commands.has_any_role("DJ", "Dj", "dj"), commands.has_permissions(administrator=True), commands.is_owner())
    async def restart(self, ctx: commands.Context):
        """Restart the currently playing song."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if player.is_paused or not player.is_connected:
            return

        try:
        	if player.is_playing:
        		await player.seek(0)
        		await ctx.send("Restarted current song.")
        	else:
        		await ctx.send("No song is playing.")
        except:
        	return

    @restart.error
    async def on_error(self, ctx, error):
    	if isinstance(error, commands.MissingAnyRole):
    		await ctx.send("You must have the `DJ` role to restart song.")
    	if isinstance(error, commands.MissingPermissions):
    		await ctx.send("You must have the `DJ` role to reatart song.")
    		
    
    @commands.command()
    @commands.check_any(commands.has_any_role("DJ", "Dj", "dj"), commands.has_permissions(administrator=True), commands.is_owner())
    async def resume(self, ctx: commands.Context):
        """Resume a currently paused player."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_paused or not player.is_connected:
            return

        try:
            await ctx.send('⏸ Player resumed.', delete_after=10)
            player.resume_votes.clear()

            return await player.set_pause(False)
        except:
        	return

    @resume.error
    async def on_error(self, ctx, error):
    	if isinstance(error, commands.MissingAnyRole):
    		await ctx.send("You must have the `DJ` role to resume the player.")
    	if isinstance(error, commands.MissingPermissions):
    		await ctx.send("You must have the `DJ` role to resume the player.")
    		
    @commands.command()
    @commands.check_any(commands.has_any_role("DJ", "Dj", "dj"), commands.has_permissions(administrator=True), commands.is_owner())
    async def skip(self, ctx: commands.Context):
        """Skip the currently playing song."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        try:
            await ctx.send('⏭ Skipped current song.', delete_after=10)
            player.skip_votes.clear()

            return await player.stop()
        except:
        	return
     
    @skip.error
    async def on_error(self, ctx, error):
    	if isinstance(error, commands.MissingAnyRole):
    		await ctx.send("You must have the `DJ` role to skip song.")
    	if isinstance(error, commands.MissingPermissions):
    		await ctx.send("You must have the `DJ` role to skip song.")
    
    @commands.command(aliases=["dc", "disconnect"])
    @commands.check_any(commands.has_any_role("DJ", "Dj", "dj"), commands.has_permissions(administrator=True), commands.is_owner())
    async def stop(self, ctx: commands.Context):
        """Stop the player and clear all internal states."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        try:
            await ctx.send('⏹ Player stopped.', delete_after=10)
            return await player.teardown()
        except:
        	return

    @stop.error
    async def on_error(self, ctx, error):
    	if isinstance(error, commands.MissingAnyRole):
    		await ctx.send("You must have the `DJ` role to stop the player.")
    	if isinstance(error, commands.MissingPermissions):
    		await ctx.send("You must have the `DJ` role to stop the player.")
    		
    @commands.command(aliases=['vol'])
    @commands.check_any(commands.has_any_role("DJ", "Dj", "dj"), commands.has_permissions(administrator=True), commands.is_owner())
    async def volume(self, ctx: commands.Context, *, vol: int):
        """Change the players volume, between 1 and 100."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if not 0 < vol < 101:
            return await ctx.send('Please enter a value between 1 and 100.')

        await player.set_volume(vol)
        await ctx.send(f'Set the volume to **{vol}**%', delete_after=7)
    
    @volume.error
    async def on_error(self, ctx, error):
    	if isinstance(error, commands.MissingAnyRole):
    		await ctx.send("You must have the `DJ` role to change volume")
    	if isinstance(error, commands.MissingPermissions):
    		await ctx.send("You must have the `DJ` role to change volume")

    @commands.command(aliases=['mix'])
    @commands.check_any(commands.has_any_role("DJ", "Dj", "dj"), commands.has_permissions(administrator=True), commands.is_owner())
    async def shuffle(self, ctx: commands.Context):
        """Shuffle the players queue."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if player.queue.qsize() < 3:
            return await ctx.send('Add more songs to the queue before shuffling.', delete_after=15)

        try:
            await ctx.send('🔀 Songs shuffled. ', delete_after=10)
            player.shuffle_votes.clear()
            return random.shuffle(player.queue._queue)
        except:
        	return
      
    @shuffle.error
    async def on_error(self, ctx, error):
    	if isinstance(error, commands.MissingAnyRole):
    		await ctx.send("You must have the `DJ` role to shuffle the playlist")
    	if isinstance(error, commands.MissingPermissions):
    		await ctx.send("You must have the `DJ` role to shuffle the playlist")
    		
    @commands.command(hidden=True)
    @commands.check_any(commands.has_any_role("DJ", "Dj", "dj"), commands.has_permissions(administrator=True), commands.is_owner())
    async def vol_up(self, ctx: commands.Context):
        """Command used for volume up button."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        vol = int(math.ceil((player.volume + 10) / 10)) * 10

        if vol > 100:
            vol = 100
            await ctx.send('Maximum volume reached', delete_after=7)

        await player.set_volume(vol)

    @vol_up.error
    async def on_error(self, ctx, error):
    	if isinstance(error, commands.MissingAnyRole):
    		await ctx.send("You must have the `DJ` role to change volume.")
    	if isinstance(error, commands.MissingPermissions):
    		await ctx.send("You must have the `DJ` role to change volume.")
    		
    @commands.command(hidden=True)
    @commands.check_any(commands.has_any_role("DJ", "Dj", "dj"), commands.has_permissions(administrator=True), commands.is_owner())
    async def vol_down(self, ctx: commands.Context):
        """Command used for volume down button."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        vol = int(math.ceil((player.volume - 10) / 10)) * 10

        if vol < 0:
            vol = 0
            await ctx.send('Player is currently muted', delete_after=10)

        await player.set_volume(vol)

    @vol_down.error
    async def on_error(self, ctx, error):
    	if isinstance(error, commands.MissingAnyRole):
    		await ctx.send("You must have the `DJ` role to change volume.")
    	if isinstance(error, commands.MissingPermissions):
    		await ctx.send("You must have the `DJ` role to change volume.")
    
    @commands.command(aliases=['eq'])
    @commands.check_any(commands.has_any_role("DJ", "Dj", "dj"), commands.has_permissions(administrator=True), commands.is_owner())
    async def equalizer(self, ctx: commands.Context, *, equalizer: str):
        """Change the players equalizer."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        eqs = {'flat': wavelink.Equalizer.flat(),
               'boost': wavelink.Equalizer.boost(),
               'metal': wavelink.Equalizer.metal(),
               'piano': wavelink.Equalizer.piano()}

        eq = eqs.get(equalizer.lower(), None)

        if not eq:
            joined = "\n".join(eqs.keys())
            return await ctx.send(f'Invalid EQ provided. Valid EQs:\n\n{joined}')

        await ctx.send(f'Successfully changed equalizer to {equalizer}', delete_after=15)
        await player.set_eq(eq)

    @equalizer.error
    async def on_error(self, ctx, error):
    	if isinstance(error, commands.MissingAnyRole):
    		await ctx.send("You must have the `DJ` role to change equalizer.")
    	if isinstance(error, commands.MissingPermissions):
    		await ctx.send("You must have the `DJ` role to change equalizer.")

    @commands.command(aliases=['que'])
    async def queue(self, ctx: commands.Context):
        """Display the players queued songs."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if player.queue.qsize() == 0:
            return await ctx.send('There are no more songs in the queue.', delete_after=15)

        entries = [track.title for track in player.queue._queue]
        pages = PaginatorSource(entries=entries)
        paginator = menus.MenuPages(source=pages, timeout=None, delete_message_after=True)

        await paginator.start(ctx)

    @commands.command(aliases=['np', 'now_playing', 'current'])
    async def nowplaying(self, ctx: commands.Context):
        """Update the player controller."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        await player.invoke_controller()

def setup(bot: commands.Bot):
    bot.add_cog(Musics(bot))
