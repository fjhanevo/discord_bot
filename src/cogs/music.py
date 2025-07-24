# cogs/music.py
import discord
from discord.ext import commands
import yt_dlp


# ytdl_format_opts: dict = {
ytdl_opts: dict = {
    'format': 'bestaudio/best',
    'quiet': True,
    'extract_flat': False,
    'skip_download': True,
    'no_playlist': True,
}

ytdl_playlist_opts: dict = {
    'extract_flat': True,
    'quiet': True,
}

ffmpeg_opts: dict = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -f s16le -ar 48000 -ac 2',
}

class Music(commands.Cog):
    """ Music player cog, capable of handling single songs as well as playlists. """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.queue = []

    async def _play_audio(self, ctx: commands.Context) -> None:
        if len(self.queue) > 0:
            song: dict = self.queue.pop(0)

            audio_src = discord.FFmpegPCMAudio(song['source'], **ffmpeg_opts)
            #NOTE: Debugging
            print(f"Audio: {type(audio_src)}")

            ctx.voice_client.play(audio_src, after=lambda e: self.bot.loop.create_task(self._play_audio(ctx)))

            await ctx.send(f"🎶Now playing: '{song['title']}' 🎶")
    
    @commands.command(name="join")
    async def join(self, ctx: commands.Context) -> None:
        if ctx.author.voice is None:
            await ctx.send("Join a voice channel first.")
            return

        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:

            # if already in channel move to users channel
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
            
        #NOTE: For debugging
        await ctx.send("v0.10")


    @commands.command(name="play")
    async def play(self, ctx: commands.Context, *, url: str) -> None:
        songs = []
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send(f"{self.user.mention}, join a voice channel first. ")

        
        with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
            try: 
                info: dict = ydl.extract_info(url, download=False)
            except Exception as e:
                await ctx.send(f"An error occured: {e}")
                return

        # Check if info is a playlist
        if "entries" in info:
            for entry in info['entries']:
                songs.append({'source': entry['url'], 'title': entry['title']})
            await ctx.send(f"Added {len(songs)} songs to the queue.")
        else:
            songs.append({'source': info['url'], 'title': info['title']})
            await ctx.send(f"Added '{info['title']}' to the queue.")

        self.queue.extend(songs)

        if not ctx.voice_client.is_playing():
            await self._play_audio(ctx)

    @commands.command(name="clear")
    async def clear(self, ctx: commands.Context) -> None:
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            ctx.voice_client.stop()
        self.queue.clear()
        
        await ctx.send("Queue cleared.")

    @commands.command(name="skip")
    async def skip(self, ctx: commands.Context) -> None:
        if ctx.voice_client.is_playing():
            await ctx.voice_client.stop()
        else:
            await ctx.send("❌No song is playing.❌")

    @commands.command(name="pause")
    async def pause(self, ctx: commands.Context) -> None:
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Paused the music.")
        else:
            await ctx.send("❌Nothing is playing right now.")

    @commands.command(name="resume")
    async def resume(self, ctx: commands.Context) -> None:
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Resumed the music.")
        else:
            await ctx.send("❌Nothing is playing right now.❌")

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
