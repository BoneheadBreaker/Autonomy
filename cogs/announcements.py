from discord.ext import commands
import discord
from cogs.shared import log, command_enabled

class AnnouncementModal(discord.ui.Modal, title="Create Announcement"):
    def __init__(self, channel: discord.TextChannel, log_manager):
        super().__init__()

        self.channel = channel
        self.log_manager = log_manager

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

    async def on_submit(self, interaction: discord.Interaction):
        title = self.title_input.value
        description = self.description_input.value

        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blurple(),
        )

        event_message = await self.channel.send(embed=embed)

        await interaction.response.send_message(
            f"Announcement created in {self.channel.mention}",
            ephemeral=True
        )

        if self.log_manager:
            log_description = (
                f"Announcement Created\n"
                f"Scheduled by {interaction.user.mention}\n"
                f"Title: {title}\n"
                f"Channel: {self.channel.mention}\n"
                f"Message ID: {event_message.id}"
            )

            await self.log_manager.add_log(
                guild_id=interaction.guild.id,
                event_name="Announcement Created",
                event_description=log_description,
                event_colour=0x008000
            )

class AnnouncementsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_manager = self.bot.get_cog("LogsManager")

    @commands.hybrid_command(name="announce")
    @command_enabled(default=True)
    @commands.has_permissions(moderate_members=True)
    async def create_event(self, ctx, channel: discord.TextChannel):
        try:

            if ctx.interaction is None:
                await ctx.send("Use slash commands for this feature.")
                return

            modal = AnnouncementModal(
                channel=channel,
                log_manager=self.log_manager,
            )

            await ctx.interaction.response.send_modal(modal)
        except Exception as error:
            print(error)

async def setup(bot):
    await bot.add_cog(AnnouncementsCog(bot))