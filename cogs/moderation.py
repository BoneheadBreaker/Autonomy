from discord.ext import commands
import discord
import datetime

from .shared import db, command_enabled


class ModerationCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    @command_enabled(default=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        try:
            await member.ban(reason=reason)
            await ctx.send(f"Banned {member.mention}")

        except Exception:
            await ctx.send("Failed to ban")

    @commands.hybrid_command(name="mute")
    @command_enabled(default=True)
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, minutes: int, *, reason="No reason provided"):
        try:
            duration = datetime.timedelta(minutes=minutes)
            await member.timeout(duration, reason=reason)
            await ctx.send(f"{member.mention} has been muted/timed out for {minutes} minutes. reason: {reason}")
        except Exception:
            await ctx.send("Failed to mute, do I have the correct permissons?")

    @commands.hybrid_command(name="unmute")
    @command_enabled(default=True)
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member, *, reason="No reason provided"):
        try:
            await member.timeout(None, reason=reason)
            await ctx.send(f"Unmuted {member.mention}, Reason: {reason}")
        except Exception:
            await ctx.send("Failed to unmute, do I have the correct permissions?")

    @commands.hybrid_group(name="warn")
    @command_enabled(default=True)
    async def warn(self, ctx):

        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid use")

    @warn.command(name="add")
    @command_enabled(default=True)
    @commands.has_permissions(moderate_members=True)
    async def warn_add(
        self,
        ctx,
        user: discord.Member,
        *,
        reason: str
    ):

        db.add(
            "warnings",
            ctx.guild.id,
            user.id,
            reason
        )

        await ctx.send(f"{user.mention} warned")

    @warn.command(name="remove")
    @command_enabled(default=True)
    @commands.has_permissions(moderate_members=True)
    async def warn_remove(
        self,
        ctx,
        user: discord.Member
    ):

        db.delete(
            "warnings",
            {
                "guild_id": ctx.guild.id,
                "user": user.id
            }
        )

        await ctx.send(
            f"Warnings removed for {user.mention}"
        )


async def setup(bot):
    await bot.add_cog(ModerationCog(bot))