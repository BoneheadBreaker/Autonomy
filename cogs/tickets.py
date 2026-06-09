import discord
from discord.ext import commands

from .shared import db, command_enabled

class TicketsTranscriptSelector(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        channel_types=[discord.ChannelType.category],
        placeholder="Select a transcripts channel",
        min_values=1,
        max_values=1,
    )
    async def select_category(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        if not interaction.user.guild_permissions.manage_guild: 
            return await interaction.response.send_message("You must have **manage_guild** permissions to configure tickets.", ephemeral=True)
        channel = select.values[0]

        

class TicketsSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        channel_types=[discord.ChannelType.category],
        placeholder="Select a category",
        min_values=1,
        max_values=1,
    )
    async def select_category(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        if not interaction.user.guild_permissions.manage_guild: 
            return await interaction.response.send_message("You must have **manage_guild** permissions to configure tickets.", ephemeral=True)
        category = select.values[0]

        await interaction.response.send_message(
            f"Selected category: {category.name}", ephemeral=True)

        embed = discord.Embed(
            title="Select the transcript channel",
            description=(
                "Select the channel where you want ticket logs to go to"
            ),
            colour=discord.Colour.blurple()
        )

        await interaction.response.send_message(
            embed=embed,
            view=LoggingSetupView(),
            ephemeral=True
        )



class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(
        name="tickets",
        description="Manage tickets"
    )
    @command_enabled(default=True)
    @commands.has_permissions(manage_guild=True)
    async def tickets(self, ctx):
        await ctx.send(
            "Please use a subcommand.\n"
            "If tickets are not already set up, use `/tickets setup`."
        )

    @tickets.command(name="setup", description="Setup tickets")
    @command_enabled(default=True)
    @commands.has_permissions(manage_guild=True)
    async def tickets_setup(self, ctx):
        embed = discord.Embed(
            title="Ticket Setup Guide",
            description="Work in progress!",
            color=discord.Color.blurple()
        )

        await ctx.send(
            embed=embed,
#            view=TicketsSetupView()
        )


async def setup(bot):
    await bot.add_cog(Tickets(bot))