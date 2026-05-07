from discord.ext import commands
import random

from .shared import command_enabled


class UtilityCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    @command_enabled(default=True)
    async def ping(self, ctx):
        await ctx.send("Pong!")

    @commands.hybrid_command(name="documentation")
    @command_enabled(default=True)
    async def documentation(self, ctx):
        await ctx.send(
            "https://boneheadbreaker.github.io/Autonomy/"
        )

    @commands.hybrid_command()
    @command_enabled(default=True)
    async def coinflip(self, ctx):

        result = (
            "Heads!"
            if random.randint(0, 1)
            else "Tails!"
        )

        await ctx.send(result)

    @commands.hybrid_command()
    @command_enabled(default=True)
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx, *, text: str):

        if ctx.interaction:

            await ctx.interaction.response.send_message(
                "Sending..",
                ephemeral=True
            )

            await ctx.channel.send(text)

        else:

            await ctx.send(text)
            await ctx.message.delete()


async def setup(bot):
    await bot.add_cog(UtilityCog(bot))