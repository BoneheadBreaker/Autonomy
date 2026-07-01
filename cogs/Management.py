import discord
from discord.ext import commands
from .shared import db

class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logs_cog = self.bot.get_cog("LogsManager")

    @commands.group(name="management", invoke_without_command=True)
    @commands.is_owner()
    async def management(self, ctx):
        await ctx.send("`.management guilds` - display all servers the bot is in\n"
                "`.management list` - display this menu\n"
                "`.management announce` - display a message in every servers configured log channel"
            )

    @management.command(name="list")
    async def list(self, ctx):
        await ctx.send("`.management guilds` - display all servers the bot is in\n"
                "`.management list` - display this menu\n"
                "`.management announce` - display a message in every servers configured log channel"
            )

    @management.command(name="announce")
    async def announce(self, ctx, *, message: str):
        try:
            """Sends an announcement to every configured log channel."""

            await ctx.send("Sending announcement...")

            total_servers = 0

            for guild in self.bot.guilds:
                try:
                    print("ABOUT TO CALL")
                    await self.logs_cog.add_log(
                        guild.id,
                        "Global Announcement",
                        message,
                        discord.Colour.blue()
                    )
                    print("FINISHED CALl")
                    total_servers += 1
                except Exception as e:
                    print(f"Failed for {guild.name}: {e}")

            await ctx.send(f"Finished. Announcement sent to {total_servers} server(s).")
        except Exception as e:
            print(e)

    @management.command(name="guilds")
    async def guilds(self, ctx):
        """List all guilds the bot is in."""

        pages = []
        current_page = ""

        guilds = sorted(self.bot.guilds, key=lambda g: g.name.lower())

        for guild in guilds:
            invite = "Unable to create invite"

            try:
                channel = discord.utils.find(
                    lambda c: (
                        isinstance(c, discord.TextChannel)
                        and c.permissions_for(guild.me).create_instant_invite
                    ),
                    guild.channels,
                )

                if channel:
                    inv = await channel.create_invite(
                        max_age=300,
                        max_uses=1,
                        unique=True,
                        reason="Bot owner requested guild list.",
                    )
                    invite = inv.url

            except discord.Forbidden:
                invite = "Missing permission"
            except Exception:
                invite = "Error creating invite"

            entry = (
                f"**{guild.name}** (`{guild.id}`)\n"
                f"Members: {guild.member_count}\n"
                f"Owner: <@{guild.owner_id}>\n"
                f"{invite}\n\n"
            )

            if len(current_page) + len(entry) > 1900:
                pages.append(current_page)
                current_page = ""

            current_page += entry

        if current_page:
            pages.append(current_page)

        if not pages:
            return await ctx.send("The bot isn't in any guilds.")

        for index, page in enumerate(pages, start=1):
            embed = discord.Embed(
                title=f"Guilds ({len(guilds)} total)",
                description=page,
                colour=discord.Color.blurple(),
            )
            embed.set_footer(text=f"Page {index}/{len(pages)}")
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Management(bot))
