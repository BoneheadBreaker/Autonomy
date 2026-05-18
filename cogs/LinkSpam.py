import re
import time
from collections import defaultdict

import discord
from discord.ext import commands

URL_REGEX = re.compile(
    r"""(?xi)
    \b(
        (?:
            https?://
            |
            www\.
        )?
        [a-z0-9.-]+\.[a-z]{2,}
        (?:
            /[^\s]*
        )?
    )
    """,
    re.IGNORECASE
)


class LinkSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.flag_manager = self.bot.get_cog("FlagManager")

        self.link_cache = defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(list)
            )
        )

        self.time_window = 30      # seconds
        self.channel_threshold = 2  # different channels required

    def normalize_link(self, url: str) -> str:
        url = url.lower().strip()

        if url.endswith("/"):
            url = url[:-1]

        return url

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild:
            return

        if message.author.bot:
            return

        links = URL_REGEX.findall(message.content)

        if not links:
            return

        guild_id = message.guild.id
        user_id = message.author.id
        channel_id = message.channel.id

        current_time = time.time()

        for raw_link in links:
            link = self.normalize_link(raw_link)

            entries = self.link_cache[guild_id][user_id][link]

            # Remove expired entries
            entries[:] = [
                (ts, ch)
                for ts, ch in entries
                if current_time - ts <= self.time_window
            ]

            # Add new occurrence
            entries.append((current_time, channel_id))

            # Count unique channels
            unique_channels = {ch for _, ch in entries}

            if len(unique_channels) >= self.channel_threshold:

                print(
                    f"[LINK SPAM] "
                    f"{message.author} in {message.guild.name}"
                )

                self.flag_manager.add_score(message.author.id, 20)

                score = self.flag_manager.get_score(message.author.id)
                print(score)

                # Clear cache so it doesn't repeatedly trigger
                self.link_cache[guild_id][user_id][link].clear()

                break


async def setup(bot):
    await bot.add_cog(LinkSpam(bot))