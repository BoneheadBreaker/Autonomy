from discord.ext import commands
import discord
import datetime

from .shared import db, command_enabled


class ModerationCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ban", description="ban a user from the server")
    @command_enabled(default=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):

        if member.guild_permissions.manage_messages or member.guild_permissions.administrator:
            await ctx.send("That user has administrator permissions, a quick quarantine command is coming soon")
            return

        try:
            await member.ban(reason=reason)
            await ctx.send(f"Banned **{member.mention}**")

        except Exception:
            await ctx.send("Failed to ban")

    async def banned_users_autocomplete(self, interaction: discord.Interaction, current: str):
        choices = []

        # Fetch bans
        async for entry in interaction.guild.bans(limit=None):
            user = entry.user

            # Match by username or ID
            if (current.lower() in user.name.lower() or current in str(user.id)):
                choices.append(
                    discord.app_commands.Choice(
                        name=f"{user} ({user.id})",
                        value=str(user.id)
                    )
                )

            # Discord only allows 25 choices
            if len(choices) >= 25:
                break

        return choices

    @commands.hybrid_command(name="unban", description="Unban a user by ID or autocomplete.")
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    @discord.app_commands.autocomplete(user_id=banned_users_autocomplete)
    async def unban(
        self,
        ctx: commands.Context,
        user_id: str,
        *,
        reason: str = "No reason provided"
    ):

        try:
            user = await self.bot.fetch_user(int(user_id))

            await ctx.guild.unban(user, reason=reason)

            await ctx.send(
                f"Successfully unbanned **{user}**\n"
                f"**Reason:** {reason}"
            )

        except ValueError:
            await ctx.send("Invalid user ID.")

        except discord.NotFound:
            await ctx.send("That user is not banned.")

        except discord.Forbidden:
            await ctx.send(
                "I do not have permission to unban members."
            )


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

    @commands.hybrid_command(name="lock", description="Lock a channel")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel

        # Set permissions for @everyone role
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(f"{channel.mention} has been locked.")

    @commands.hybrid_command(name="unlock", description="Unlocks a channe;")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel

        # Reset permissions or set to True
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(f"{channel.mention} has been unlocked.")


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