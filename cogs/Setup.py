import discord
from discord.ext import commands

class SetupDialog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(f"Added to {guild.name} ({guild.id})")

        system_channel = guild.system_channel

        setup_message = (
            "Hi, Thanks for adding me\n"
            "This feature is still a work in progress!"
        )

        embed = discord.Embed(
            title="Setup",
            description=setup_message,
            colour=0x00ff00
        )

        if system_channel and system_channel.permissions_for(guild.me).send_messages:
            await system_channel.send(embed=embed)
        else:
            # Fallback incase system channel not set
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    await channel.send(embed=embed)
                    break

async def setup(bot):
    await bot.add_cog(SetupDialog(bot))