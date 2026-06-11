import discord
from discord.ext import commands

from .shared import db, command_enabled


class PanelMessageModal(discord.ui.Modal, title="Ticket Panel Setup"):

    panel_message = discord.ui.TextInput(
        label="Panel Message",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=4000
    )

    ticket_limit = discord.ui.TextInput(
        label="Ticket Limit Per User",
        required=True,
        default="1"
    )

    def __init__(self, category_id, transcript_id, panel_channel_id):
        super().__init__()
        self.category_id = category_id
        self.transcript_id = transcript_id
        self.panel_channel_id = panel_channel_id

    async def on_submit(self, interaction: discord.Interaction):

        guild = interaction.guild

        db.delete("tickets", {"guild_id": guild.id})

        db.add(
            "tickets",
            guild.id,
            self.transcript_id,
            self.category_id,
            int(self.ticket_limit.value)
        )

        panel_channel = guild.get_channel(self.panel_channel_id)

        embed = discord.Embed(
            title="Support Tickets",
            description=str(self.panel_message),
            colour=discord.Colour.blurple()
        )

        msg = await panel_channel.send(
            embed=embed,
            view=TicketPanelView()
        )

        db.delete("ticket_panels", {"guild_id": guild.id})

        db.add(
            "ticket_panels",
            guild.id,
            panel_channel.id,
            msg.id,
            str(self.panel_message)
        )

        await interaction.response.send_message(
            "Ticket system configured.",
            ephemeral=True
        )


class PanelChannelSelector(discord.ui.View):

    def __init__(self, category_id, transcript_id):
        super().__init__(timeout=180)
        self.category_id = category_id
        self.transcript_id = transcript_id

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        channel_types=[discord.ChannelType.text],
        placeholder="Select panel channel",
        min_values=1,
        max_values=1
    )
    async def select_channel(self, interaction, select):

        channel = select.values[0]

        await interaction.response.send_modal(
            PanelMessageModal(
                self.category_id,
                self.transcript_id,
                channel.id
            )
        )


class TranscriptSelector(discord.ui.View):

    def __init__(self, category_id):
        super().__init__(timeout=180)
        self.category_id = category_id

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        channel_types=[discord.ChannelType.text],
        placeholder="Select transcript channel",
        min_values=1,
        max_values=1
    )
    async def select_channel(self, interaction, select):

        channel = select.values[0]

        await interaction.response.send_message(
            embed=discord.Embed(
                title="Panel Channel",
                description="Select where the ticket panel should be posted.",
                colour=discord.Colour.blurple()
            ),
            view=PanelChannelSelector(self.category_id, channel.id),
            ephemeral=True
        )


class TicketCategorySelector(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        channel_types=[discord.ChannelType.category],
        placeholder="Select ticket category",
        min_values=1,
        max_values=1
    )
    async def select_category(self, interaction, select):

        category = select.values[0]

        await interaction.response.send_message(
            embed=discord.Embed(
                title="Transcript Channel",
                description="Select where transcripts should be sent.",
                colour=discord.Colour.blurple()
            ),
            view=TranscriptSelector(category.id),
            ephemeral=True
        )


class TicketCloseView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Close Ticket",
        style=discord.ButtonStyle.red,
        custom_id="close_ticket"
    )
    async def close_ticket(self, interaction, button):

        ticket = db.get(
            "active_tickets",
            {
                "guild_id": interaction.guild.id,
                "channel_id": interaction.channel.id
            }
        )

        if not ticket:
            return await interaction.response.send_message(
                "This isn't a ticket.",
                ephemeral=True
            )

        config = db.get("tickets", {"guild_id": interaction.guild.id})

        transcript_channel = interaction.guild.get_channel(config[0][1])

        messages = []
        async for msg in interaction.channel.history(limit=None, oldest_first=True):
            messages.append(f"{msg.author}: {msg.content}")

        embed = discord.Embed(
            title="Ticket Transcript",
            description="\n".join(messages)[:4000] or "No messages.",
            colour=discord.Colour.blurple()
        )

        await transcript_channel.send(embed=embed)

        db.delete(
            "active_tickets",
            {
                "guild_id": interaction.guild.id,
                "channel_id": interaction.channel.id
            }
        )

        await interaction.response.send_message("Closing ticket...")
        await interaction.channel.delete()


class TicketPanelView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Create Ticket",
        style=discord.ButtonStyle.blurple,
        custom_id="create_ticket"
    )
    async def create_ticket(self, interaction, button):

        guild = interaction.guild

        config = db.get("tickets", {"guild_id": guild.id})

        if not config:
            return await interaction.response.send_message(
                "Tickets not configured.",
                ephemeral=True
            )

        category = guild.get_channel(config[0][2])
        limit = config[0][3]

        existing = db.get(
            "active_tickets",
            {
                "guild_id": guild.id,
                "owner_id": interaction.user.id
            }
        )

        if len(existing) >= limit:
            return await interaction.response.send_message(
                "You reached the ticket limit.",
                ephemeral=True
            )

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
        }

        channel = await guild.create_text_channel(
            f"{interaction.user.name}-ticket",
            category=category,
            overwrites=overwrites
        )

        db.add("active_tickets", guild.id, channel.id, interaction.user.id)

        await channel.send(
            embed=discord.Embed(
                title="Ticket Created",
                description=interaction.user.mention,
                colour=discord.Colour.green()
            ),
            view=TicketCloseView()
        )

        await interaction.response.send_message(
            f"Created {channel.mention}",
            ephemeral=True
        )


class Tickets(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(name="tickets", description="Manage tickets")
    @command_enabled(default=True)
    @commands.has_permissions(manage_guild=True)
    async def tickets(self, ctx):
        pass

    @tickets.command(name="setup")
    async def setup(self, ctx):

        existing = db.get("tickets", {"guild_id": ctx.guild.id})

        if existing:
            await ctx.send(
                embed=discord.Embed(
                    title="Warning",
                    description="Already configured. Running again overwrites.",
                    colour=discord.Colour.orange()
                )
            )

        await ctx.send(
            embed=discord.Embed(
                title="Ticket Setup",
                description="Select a category.",
                colour=discord.Colour.blurple()
            ),
            view=TicketCategorySelector()
        )


async def setup(bot):
    await bot.add_cog(Tickets(bot))