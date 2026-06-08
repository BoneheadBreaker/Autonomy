import discord
from discord.ext import commands

from .shared import db, command_enabled

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
    async def select_category(
        self,
        interaction: discord.Interaction,
        select: discord.ui.ChannelSelect,
    ):
        category = select.values[0]

        await interaction.response.send_message(
            f"Selected category: {category.name}",
            ephemeral=True,
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

    @tickets.command(
        name="setup",
        description="Setup tickets"
    )
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