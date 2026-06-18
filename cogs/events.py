from discord.ext import commands
import discord
from datetime import datetime, UTC, timedelta
import re

from cogs.shared import log, command_enabled

DURATION_RE = re.compile(r"(\d+)([wdhm])")


def parse_duration(text: str) -> timedelta:
    total = timedelta()

    for amount, unit in DURATION_RE.findall(text.lower()):
        amount = int(amount)

        if unit == "w":
            total += timedelta(weeks=amount)
        elif unit == "d":
            total += timedelta(days=amount)
        elif unit == "h":
            total += timedelta(hours=amount)
        elif unit == "m":
            total += timedelta(minutes=amount)

    if total.total_seconds() == 0:
        raise ValueError("Invalid duration")

    return total

class EventView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.attending = set()
        self.maybe = set()
        self.not_attending = set()

    async def update_embed(self, interaction: discord.Interaction):
        embed = interaction.message.embeds[0]

        attending_text = (
            "\n".join(f"<@{uid}>" for uid in self.attending)
            if self.attending else "Nobody"
        )

        maybe_text = (
            "\n".join(f"<@{uid}>" for uid in self.maybe)
            if self.maybe else "Nobody"
        )

        not_attending_text = (
            "\n".join(f"<@{uid}>" for uid in self.not_attending)
            if self.not_attending else "Nobody"
        )

        embed.set_field_at(
            3,
            name=f"Attending ({len(self.attending)})",
            value=attending_text,
            inline=True
        )

        embed.set_field_at(
            4,
            name=f"Maybe ({len(self.maybe)})",
            value=maybe_text,
            inline=True
        )

        embed.set_field_at(
            5,
            name=f"Not Attending ({len(self.not_attending)})",
            value=not_attending_text,
            inline=True
        )

        await interaction.message.edit(embed=embed, view=self)

    @discord.ui.button(label="Attending", emoji="✅", style=discord.ButtonStyle.success)
    async def attending_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id

        self.maybe.discard(uid)
        self.not_attending.discard(uid)
        self.attending.add(uid)

        await interaction.response.defer()
        await self.update_embed(interaction)

    @discord.ui.button(label="Maybe", emoji="❔", style=discord.ButtonStyle.secondary)
    async def maybe_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id

        self.attending.discard(uid)
        self.not_attending.discard(uid)
        self.maybe.add(uid)

        await interaction.response.defer()
        await self.update_embed(interaction)

    @discord.ui.button(label="Not Attending", emoji="❌", style=discord.ButtonStyle.danger)
    async def not_attending_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id

        self.attending.discard(uid)
        self.maybe.discard(uid)
        self.not_attending.add(uid)

        await interaction.response.defer()
        await self.update_embed(interaction)

class EventCreateModal(discord.ui.Modal, title="Schedule Event"):
    def __init__(self, channel: discord.TextChannel, log_manager, role: discord.Role | None = None):
        super().__init__()

        self.channel = channel
        self.log_manager = log_manager
        self.role = role

    title_input = discord.ui.TextInput(
        label="Title",
        required=True,
        max_length=100,
    )

    description_input = discord.ui.TextInput(
        label="Description",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000,
    )

    starts_in_input = discord.ui.TextInput(
        label="Starts In (optional)",
        required=False,
        max_length=50,
    )

    start_date_input = discord.ui.TextInput(
        label="Start Date (UTC) optional",
        placeholder="YYYY-MM-DD HH:MM",
        required=False,
        max_length=50,
    )

    duration_input = discord.ui.TextInput(
        label="Duration",
        required=True,
        max_length=50,
    )

    async def on_submit(self, interaction: discord.Interaction):
        title = self.title_input.value
        description = self.description_input.value
        starts_in = self.starts_in_input.value.strip()
        start_date = self.start_date_input.value.strip()
        duration_text = self.duration_input.value

        # validation
        if starts_in and start_date:
            await interaction.response.send_message(
                "❌ Use either Starts In OR Start Date, not both.",
                ephemeral=True
            )
            return

        if not starts_in and not start_date:
            await interaction.response.send_message(
                "❌ You must provide a start time.",
                ephemeral=True
            )
            return

        try:
            duration = parse_duration(duration_text)
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid duration format.",
                ephemeral=True
            )
            return

        try:
            if starts_in:
                start_time = datetime.now(UTC) + parse_duration(starts_in)
            else:
                start_time = datetime.strptime(
                    start_date,
                    "%Y-%m-%d %H:%M"
                ).replace(tzinfo=UTC)

        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid start date format.",
                ephemeral=True
            )
            return

        # prevent past events
        if start_time < datetime.now(UTC):
            await interaction.response.send_message(
                "❌ Start time must be in the future.",
                ephemeral=True
            )
            return

        end_time = start_time + duration

        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blurple(),
        )

        embed.add_field(
            name="Starts",
            value=f"<t:{int(start_time.timestamp())}:F>\n<t:{int(start_time.timestamp())}:R>",
            inline=False
        )

        embed.add_field(
            name="Ends",
            value=f"<t:{int(end_time.timestamp())}:F>\n<t:{int(end_time.timestamp())}:R>",
            inline=False
        )

        embed.add_field(
            name="Duration",
            value=duration_text,
            inline=False
        )

        # RSVP fields (IMPORTANT ORDER = fixed indexes)
        embed.add_field(name="Attending (0)", value="Nobody", inline=True)
        embed.add_field(name="Maybe (0)", value="Nobody", inline=True)
        embed.add_field(name="Not Attending (0)", value="Nobody", inline=True)

        view = EventView()

        event_message = await self.channel.send(
            content=self.role.mention if self.role else None,
            embed=embed,
            view=view
        )

        await interaction.response.send_message(
            f"✅ Event created in {self.channel.mention}",
            ephemeral=True
        )

        if self.log_manager:
            log_description = (
                f"Event scheduled\n"
                f"Scheduled by {interaction.user.mention}\n"
                f"Title: {title}\n"
                f"Channel: {self.channel.mention}\n"
                f"Role Ping: {self.role.mention if self.role else 'None'}\n"
                f"Starts: {start_time.isoformat()}\n"
                f"Ends: {end_time.isoformat()}\n"
                f"Duration: {duration_text}\n"
                f"Message ID: {event_message.id}"
            )

            await self.log_manager.add_log(
                guild_id=interaction.guild.id,
                event_name="Event Scheduled",
                event_description=log_description,
                event_colour=0x008000
            )

class EventCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_manager = self.bot.get_cog("LogsManager")

    @commands.hybrid_group(name="event")
    @command_enabled(default=True)
    async def event(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use `/event create #channel @role`")

    @event.command(name="create")
    @command_enabled(default=True)
    @commands.has_permissions(moderate_members=True)
    async def create_event(self, ctx, channel: discord.TextChannel, role: discord.Role | None = None):

        if ctx.interaction is None:
            await ctx.send("Use slash commands for this feature.")
            return

        modal = EventCreateModal(
            channel=channel,
            log_manager=self.log_manager,
            role=role
        )

        await ctx.interaction.response.send_modal(modal)

    @create_event.error
    async def create_event_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You need Moderate Members permission.")


async def setup(bot):
    await bot.add_cog(EventCog(bot))