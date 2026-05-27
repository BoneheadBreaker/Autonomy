import discord
from discord.ext import commands

class SetupDialogView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Configure Logging", style=discord.ButtonStyle.primary, custom_id="configure_logging")
    async def configure_logging(self, interaction: discord.Interaction, button: discord.ui.Button):

        configure_logging_message = (
            "Hey!\n"
            "This feature is still a work in progress!"
        )

        embed = discord.Embed(
            title="Setup",
            description=configure_logging_message,
            colour=0x00ff00
        )

        system_channel = interaction.guild.system_channel

        if system_channel and system_channel.permissions_for(interaction.guild.me).send_messages:
            await system_channel.send(embed=embed)
        else:
            # Fallback incase system channel not set
            for channel in interaction.guild.text_channels:
                if channel.permissions_for(interaction.guild.me).send_messages:
                    await channel.send(embed=embed)
                    break

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
            await system_channel.send(embed=embed, view=SetupDialogView())
        else:
            # Fallback incase system channel not set
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    await channel.send(embed=embed, view=SetupDialogView())
                    break

async def setup(bot):
    await bot.add_cog(SetupDialog(bot))