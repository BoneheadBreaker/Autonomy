import discord
from discord.ext import commands
from typing import Optional

from .shared import command_enabled


class CustomEmbeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(
        name="embeds",
        description="Manage embeds"
    )
    @command_enabled(default=True)
    @commands.has_permissions(administrator=True)
    async def embeds(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                "Please use a subcommand.\n"
                "`/embeds create`"
            )

    @embeds.command(
        name="create",
        description="Create a custom embed"
    )
    @command_enabled(default=True)
    @commands.has_permissions(administrator=True)
    async def create(
        self,
        ctx: commands.Context,
        text: str,
        color: Optional[discord.Color] = None,
        image: Optional[discord.Attachment] = None,
    ):
        if color is None:
            color = discord.Color.blurple()

        embed = discord.Embed(
            description=text,
            color=color
        )

        file = None

        if image is not None:
            file = await image.to_file()
            embed.set_image(url=f"attachment://{file.filename}")

        await ctx.send(embed=embed, file=file)

        # Delete the original message only for prefix commands
        if ctx.interaction is None:
            try:
                await ctx.message.delete()
            except (discord.Forbidden, discord.NotFound):
                pass


async def setup(bot):
    await bot.add_cog(CustomEmbeds(bot))
