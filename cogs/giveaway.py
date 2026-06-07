import random
import discord
from discord.ext import commands
from .shared import command_enabled


class GiveAway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="giveaway", description="Create an instant giveaway, it immediately picks the winners")
    @command_enabled(default=True)
    @commands.has_permissions(manage_guild=True)
    async def giveaway(
        self,
        ctx,
        prize: str,
        winners: int = 1,
        role: discord.Role = None
    ):
        guild = ctx.guild

        if guild is None:
            return await ctx.send("This command can only be used in a server.")

        # Choose members source
        members_selection = role.members if role else guild.members

        # Filter bots out
        filtered_members = [m for m in members_selection if not m.bot]

        # No participants
        if not filtered_members:
            return await ctx.send("No eligible members for this giveaway.")

        # Too many winners requested
        if len(filtered_members) <= winners:
            return await ctx.send(
                f"Giveaway canceled: only {len(filtered_members)} eligible members "
                f"for {winners} winner(s)."
            )

        # Pick unique winners
        winners_list = []

        while len(winners_list) < winners:
            winner = random.choice(filtered_members)

            if winner.id not in winners_list:
                winners_list.append(winner.id)
                await ctx.send(f"🎉 Winner for **{prize}**: {winner.mention}")

        return


async def setup(bot):
    await bot.add_cog(GiveAway(bot))