import discord
from discord.ext import commands

from .shared import db


class JoinLeave(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # -------------------------
    # Helpers
    # -------------------------

    def is_enabled(
        self,
        guild_id: int
    ) -> bool:

        rows = db.get(
            "modules_is_enabled",
            {
                "guild_id": guild_id,
                "module": "joinleave"
            }
        )

        if not rows:
            return True

        return bool(rows[0][2])

    def get_channel(
        self,
        guild: discord.Guild
    ):

        rows = db.get(
            "joinleave_channel",
            {
                "guild_id": guild.id
            }
        )

        if not rows:
            return None

        try:
            channel_id = int(rows[0][1])
        except (TypeError, ValueError):
            return None

        return guild.get_channel(
            channel_id
        )

    # -------------------------
    # Embed Builders
    # -------------------------

    def build_join_embed(
        self,
        member: discord.Member
    ):

        embed = discord.Embed(
            title="🎉 Member Joined",
            colour=discord.Colour.green(),
            timestamp=discord.utils.utcnow()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        if member.guild.icon:
            embed.set_author(
                name=member.guild.name,
                icon_url=member.guild.icon.url
            )

        embed.add_field(
            name="Member",
            value=f"{member.mention}\n`{member}`",
            inline=False
        )

        embed.add_field(
            name="Account Created",
            value=discord.utils.format_dt(
                member.created_at,
                style="R"
            ),
            inline=True
        )

        embed.add_field(
            name="Member Count",
            value=str(
                member.guild.member_count
            ),
            inline=True
        )

        account_age = (
            discord.utils.utcnow()
            - member.created_at
        ).days

        if account_age < 7:

            embed.add_field(
                name="⚠️ New Account",
                value=f"{account_age} day(s) old",
                inline=False
            )

        embed.set_footer(
            text=f"User ID: {member.id}"
        )

        return embed

    def build_leave_embed(
        self,
        member: discord.Member
    ):

        embed = discord.Embed(
            title="👋 Member Left",
            colour=discord.Colour.orange(),
            timestamp=discord.utils.utcnow()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        if member.guild.icon:
            embed.set_author(
                name=member.guild.name,
                icon_url=member.guild.icon.url
            )

        embed.add_field(
            name="Member",
            value=f"`{member}`",
            inline=False
        )

        if member.joined_at:

            embed.add_field(
                name="Joined Server",
                value=discord.utils.format_dt(
                    member.joined_at,
                    style="R"
                ),
                inline=True
            )

        embed.add_field(
            name="Account Created",
            value=discord.utils.format_dt(
                member.created_at,
                style="R"
            ),
            inline=True
        )

        embed.set_footer(
            text=f"User ID: {member.id}"
        )

        return embed

    # -------------------------
    # Events
    # -------------------------

    @commands.Cog.listener()
    async def on_member_join(
        self,
        member: discord.Member
    ):

        if not self.is_enabled(
            member.guild.id
        ):
            return

        channel = self.get_channel(
            member.guild
        )

        if not channel:
            return

        try:

            await channel.send(
                embed=self.build_join_embed(
                    member
                )
            )

        except discord.HTTPException:
            pass

    @commands.Cog.listener()
    async def on_member_remove(
        self,
        member: discord.Member
    ):

        if not self.is_enabled(
            member.guild.id
        ):
            return

        channel = self.get_channel(
            member.guild
        )

        if not channel:
            return

        try:

            await channel.send(
                embed=self.build_leave_embed(
                    member
                )
            )

        except discord.HTTPException:
            pass


async def setup(bot):

    await bot.add_cog(
        JoinLeave(bot)
    )