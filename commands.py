from discord.ext import commands

def handle_commands(bot):
    @bot.hybrid_command()
    async def ping(ctx):
        await ctx.send("Pong!")