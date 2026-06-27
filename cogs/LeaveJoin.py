import discord
from discord.ext import commands
from typing import Optional

from .shared import db


class JoinLeave(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # -------------------------
    # Database Helpers
    # -------------------------

    def is_enabled(self, guild_id: int) -> bool:
        """Checks if the join/leave module is enabled for the guild."""
        rows = db.get(
            "modules_is_enabled",
            {"guild_id": guild_id, "module": "joinleave"}
        )
        return bool(rows[0][2]) if rows else True

    def get_channel(self, guild: discord.Guild) -> Optional[discord.TextChannel]:
        """Fetches the designated log channel from the database."""
        rows = db.get("joinleave_channel", {"guild_id": guild.id})
        
        if not rows:
            return None

        try:
            channel_id = int(rows[0][1])
            return guild.get_channel(channel_id)
        except (TypeError, ValueError):
            return None

    # -------------------------
    # Modern Embed Builders
    # -------------------------

    def build_join_embed(self, member: discord.Member) -> discord.Embed:
        """Builds an advanced, aesthetically pleasing welcome embed."""
        
        # Using a sleek blurple/cyan color instead of basic green
        embed = discord.Embed(
            title=f"Welcome to {member.guild.name}! 🎉",
            description=f"Hey {member.mention}, thanks for dropping in!\nYou are our **{member.guild.member_count}th** member.",
            colour=0x5865F2, 
            timestamp=discord.utils.utcnow()
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        # Calculate account age for security profiling
        account_age = (discord.utils.utcnow() - member.created_at).days

        # Advanced Security Flags
        if account_age < 1:
            embed.colour = discord.Colour.red()
            embed.add_field(
                name="🚨 Security Alert",
                value="This account was created **less than 24 hours ago**.",
                inline=False
            )
        elif account_age < 7:
            embed.colour = discord.Colour.gold()
            embed.add_field(
                name="⚠️ New Account",
                value=f"Account is only {account_age} day(s) old.",
                inline=False
            )
        else:
            embed.add_field(
                name="Account Created",
                value=discord.utils.format_dt(member.created_at, style="R"),
                inline=True
            )

        embed.set_footer(
            text=f"User ID: {member.id}",
            icon_url=member.guild.icon.url if member.guild.icon else None
        )

        return embed

    def build_leave_embed(self, member: discord.Member) -> discord.Embed:
        """Builds a clean, informative leave embed."""
        
        embed = discord.Embed(
            description=f"**{member.name}** (`{member.id}`) has left the server.",
            colour=0x2B2D31, # Uses Discord's native dark mode background color
            timestamp=discord.utils.utcnow()
        )

        embed.set_author(
            name="Member Departed 🕊️", 
            icon_url=member.display_avatar.url
        )

        # Only add the "Joined" field if the data is available
        if member.joined_at:
            time_stayed = (discord.utils.utcnow() - member.joined_at).days
            embed.add_field(
                name="Time Spent Here",
                value=f"{time_stayed} day(s)",
                inline=True
            )

        embed.add_field(
            name="Joined Server",
            value=discord.utils.format_dt(member.joined_at, style="R") if member.joined_at else "Unknown",
            inline=True
        )

        return embed

    # -------------------------
    # Event Listeners
    # -------------------------

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if not self.is_enabled(member.guild.id):
            return

        channel = self.get_channel(member.guild)
        if not channel:
            return

        # Advanced: Check if the bot actually has permission to send embeds here!
        perms = channel.permissions_for(member.guild.me)
        if not perms.send_messages or not perms.embed_links:
            return

        try:
            # We add `content=member.mention` so the user actually gets a ping notification
            await channel.send(
                content=member.mention,
                embed=self.build_join_embed(member)
            )
        except discord.HTTPException:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if not self.is_enabled(member.guild.id):
            return

        channel = self.get_channel(member.guild)
        if not channel:
            return

        perms = channel.permissions_for(member.guild.me)
        if not perms.send_messages or not perms.embed_links:
            return

        try:
            await channel.send(embed=self.build_leave_embed(member))
        except discord.HTTPException:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(JoinLeave(bot))
