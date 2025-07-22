# cogs/music.py
import discord
from discord.ext import commands
import yt_dlp

class Music(commands.Cog):
    """ A cog to deal with playing music. """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queue = {}

    def _get_queue(self, guild_id: int):
        """ Helper function to get the queue, or create one if one doesn't exist """
        if guild_id not in self.queue:
            self.queue[guild_id] = []
        return self.queue[guild_id]
    
    def _play_next(self, ctx: commands.Context):
        guild_id = ctx.guild.id
        queue = self._get_queue(guild_id)

        if not queue:
            return

        song = queue.pop(0)
        video_url = song['stream_url']

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1',
            'options': '-vn'
        }
        audio_source = discord.FFmpegPCMAudio(video_url, **ffmpeg_options)

        ctx.voice_client.play(audio_source, after=lambda e: self._play_next(ctx))



    @commands.command()
    async def join(self, ctx: commands.Context):
        if ctx.author.voice is None:
            await ctx.send("You are currently not in a voice channel.")
            return 
        
        channel = ctx.author.voice.channel

        if ctx.voice_client is not None:
            # Move to user's channel if already in a channel
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()

        await ctx.send(f"Joined {channel.name}")

    @commands.command()
    async def leave(self, ctx: commands.Context):
        if ctx.voice_client:
            await ctx.voice_client.disconnect(force=True)
            # clear queue if bot leaves
            if ctx.guild.id in self.queue:
                del self.queue[ctx.guild.id]


    @commands.command()
    async def play(self, ctx: commands.Context, *, url: str):
        # check if audio is playing 
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.voice.channel.connect()
            else:
                await ctx.send(f"{ctx.author.mention}, join a voice channel first.")
                return

        queue = self._get_queue(ctx.guild.id)

        ydl_options = {'format': 'bestaudio/best', 'quiet': True}

        try:
            with yt_dlp.YoutubeDL(ydl_options) as ydl:
                info = ydl.extract_info(url, download=False, process=False)

                # Check for playlist
                if 'entries' in info:
                    for entry in info['entries']:
                        entry_info = ydl.extract_info(entry['url'], download=False, process=False)
                        song = {
                            'title': entry_info.get('title', 'Unknown Title'),
                            'video_url': entry_info['url']
                        }
                        queue.append(song)
                # Handle single video request
                else:
                    song = {
                        'title': info.get('title', 'Unknown Title'),
                        'video_url': info['url']
                    }
                    #TODO: Implement overwriting capabilites
                    ...
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

        if not ctx.voice_client.is_playing():
            self._play_next(ctx)

    #TODO: Implement !skip and !queue

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
