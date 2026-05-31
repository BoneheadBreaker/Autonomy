import re
import time
from collections import defaultdict
from .shared import log
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
        self.log_manager = self.bot.get_cog("LogsManager")

        self.link_cache = defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(list)
            ))

        self.time_window = 10      # seconds
        self.channel_threshold = 3  # different channels required

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
                (ts, ch, msg)
                for ts, ch, msg in entries
                if current_time - ts <= self.time_window
            ]

            # Store the message itself
            entries.append((current_time, channel_id, message))

            unique_channels = {ch for _, ch, _ in entries}

            if len(unique_channels) >= self.channel_threshold:

                self.flag_manager.add_score(message.author.id, 20)
                start_time = min(ts for ts, _, _ in entries)
                end_time = max(ts for ts, _, _ in entries)

                duration = end_time - start_time
                log("Test")

                if self.log_manager:
                    description = (
                        f"{len(entries)} messages were sent in {len(unique_channels)} unique channels in {duration} seconds \n"
                        f"Autonomy has automatically deleted them"
                    )

                    await self.log_manager.add_log(guild_id=message.guild.id, event_name="Log - Link spammed", event_description=description, event_colour=0xff0000)
                else:
                    log("Log manager cannot be found")
                # Delete every tracked message for this link
                for _, _, msg in entries:
                    try:
                        await msg.delete()
                    except discord.NotFound:
                        pass
                    except discord.Forbidden:
                        pass
                    except discord.HTTPException:
                        pass

                self.link_cache[guild_id][user_id][link].clear()

                break


async def setup(bot):
    await bot.add_cog(LinkSpam(bot))