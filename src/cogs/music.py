# cogs/music.py
import discord
from discord.ext import commands
import yt_dlp
import asyncio


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

            if 'source' not in song:
                try:
                    with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                        info: dict = await asyncio.to_thread(
                            lambda: ydl.extract_info(song['webpage_url'], download=False)
                        )
                        song['source'] = info['url']
                except Exception as e:
                    await ctx.send(f"Error processing song {song['title']}: {e}")
                    await self._play_audio(ctx)
                    return

            if ctx.voice_client:
                audio_src: discord.player.FFmpegPCMAudio = discord.FFmpegPCMAudio(song['source'], **ffmpeg_opts)
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
            
    @commands.command(name="leave")
    async def leave(self, ctx: commands.Context) -> None:
        if ctx.voice_client is None:
            await ctx.send("Not in a channel.")
            return

        await ctx.voice_client.disconnect(force=False)


    @commands.command(name="play")
    async def play(self, ctx: commands.Context, *, url: str) -> None:
        # songs = []
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send(f"{self.user.mention}, join a voice channel first. ")

        if "playlist?list=" in url:
            with yt_dlp.YoutubeDL(ytdl_playlist_opts) as ydl:
                info: dict = ydl.extract_info(url, download=False)
                for entry in info['entries']:
                    self.queue.append({'webpage_url': entry['url'], 'title': entry.get('title', 'Unknown title')})
            await ctx.send(f"✅ Added {len(info['entries'])} songs to the queue.")

        else:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                info: dict = ydl.extract_info(url, download=False)
                self.queue.append({'webpage_url': info['url'], 'title': info.get('title', 'Unknown title')})
        
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
