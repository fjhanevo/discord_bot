# cogs/utils.py
import discord
from discord.ext import commands
import asyncio

class Utils(commands.Cog):
    """ A Cog for handling utility functionality. """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    # The before and after parameters needs to be present for the function to work
    @commands.Cog.listener()
    async def on_voice_state_update(
        self, member: discord.Member,
        before: discord.VoiceState, after: discord.VoiceState    
    ) -> None:
        """
        Check if the bot is the only member in the voice
        channel, if it is, disconnects after 2 minutes.
        """
        if member.id == self.bot.user.id:
            return
        
        vc: discord.voice_client.VoiceClient  = member.guild.voice_client

        if vc and len(vc.channel.members) == 1:
            await asyncio.sleep(20)

            if len(vc.channel.members) == 1:
                await vc.disconnect(force=False)

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



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utils(bot))
