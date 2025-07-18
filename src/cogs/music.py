# cogs/music.py
import discord
from discord.enums import E
from discord.ext import commands
import yt_dlp

class Music(commands.Cog):
    """ A cog to deal with playing music. """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        #TODO: implement playlist functionality
        # self.queue = []

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
        if ctx.voice_client is None:
            await ctx.send("I'm not in a voice channel!")
            return
        
        await ctx.voice_client.disconnect(force=True)


    async def _play_audio(self, ctx: commands.Context, url: str):
        """ Helper function to queue and play audio """
        
        ydl_options= {
            'format': 'bestaudio/best',
            'quiet': True,
            'extract_flat': False,
        }

        #TODO: implement this later for dealing with playlists
        # guild_id = ctx.guild.id
        # if guild_id not in self.queue:
        #     self.queue[guild_id] = []

        try: 
            with yt_dlp.YoutubeDL(ydl_options) as ydl:
                info = ydl.extract_info(url, download=False) 
                video_url = info['url']
                video_title = info.get('title', 'Unknown title')
        except Exception as e:
            await ctx.send(f"Error with url: {e}")
            return
        
        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1',
            'options': '-vn'
        }

        audio_source = discord.FFmpegPCMAudio(video_url, **ffmpeg_options)

        ctx.voice_client.play(audio_source)


    @commands.command()
    async def play(self, ctx: commands.Context, *, url: str):
        # check if audio is playing 
        if ctx.voice_client is None:
            if ctx.author.voice:
                voice_channel = ctx.author.voice.channel
                await voice_channel.connect()
            else:
                await ctx.send(f"{ctx.author.mention}, join a voice channel first.")
                return

        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            ctx.voice_client.stop()

        await self._play_audio(ctx, url)

