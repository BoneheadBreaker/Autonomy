import discord
from discord.ext import commands

from .shared import db


class LinkFilter(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        print("COGG ADDEDDDD")

    @commands.Cog.listener()
    async def on_message(self, message):
        print("SEEEN MESSAGEE")
        if message.author.bot:
            return

        if not message.guild:
            return

        if message.author.guild_permissions.manage_messages:
            return

        rows = db.get(
            "blocked_links",
            {
                "guild_id": message.guild.id
            }
        )
        print(rows)
        print(message.guild.id)
        print(message.content)
        if not rows:
            return

        content = message.content.lower()

        for _, blocked_link in rows:

            if blocked_link.lower() in content:

                try:
                    await message.delete()

                    try:
                        await message.author.send(
                            f"Your message was removed because it contained a blocked link\n"
                        )
                    except Exception:
                        pass

                except discord.Forbidden:
                    pass

                break


async def setup(bot):
    await bot.add_cog(LinkFilter(bot))