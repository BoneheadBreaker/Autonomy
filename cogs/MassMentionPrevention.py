import time
from collections import defaultdict, deque

import discord
from discord.ext import commands


class AntiMassMention(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # limits
        self.user_limit = 4
        self.role_limit = 3
        self.total_limit = 6

        # allow @everyone / @here
        self.allow_everyone = False

        # rolling time window (seconds)
        self.window = 10

        # user_id -> deque[(timestamp, message)]
        self.mention_cache = defaultdict(deque)

    def cleanup_old_entries(self, user_id: int):
        now = time.time()
        dq = self.mention_cache[user_id]

        while dq and now - dq[0][0] > self.window:
            dq.popleft()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author.bot:
            return

        if not message.guild:
            return

        user_mentions = len(message.mentions)
        role_mentions = len(message.role_mentions)
        everyone = 1 if message.mention_everyone else 0

        # ignore messages without mentions
        if user_mentions == 0 and role_mentions == 0 and everyone == 0:
            return

        # instantly block @everyone / @here
        if everyone and not self.allow_everyone:
            try:
                await message.delete()

                await message.channel.send(
                    f"{message.author.mention} @ everyone and @ here are not allowed.",
                    delete_after=5
                )

            except discord.Forbidden:
                print("Missing Manage Messages permission")

            except discord.HTTPException as e:
                print(f"Delete failed: {e}")

            return

        user_id = message.author.id

        # cleanup expired entries
        self.cleanup_old_entries(user_id)

        dq = self.mention_cache[user_id]

        # store current message
        dq.append((time.time(), message))

        total_users = 0
        total_roles = 0
        total_everyone = 0

        # calculate totals in rolling window
        for _, msg in dq:
            total_users += len(msg.mentions)
            total_roles += len(msg.role_mentions)

            if msg.mention_everyone:
                total_everyone += 1

        total_mentions = total_users + total_roles + total_everyone

        print(
            f"[MENTION WINDOW] "
            f"user={message.author} "
            f"users={total_users} "
            f"roles={total_roles} "
            f"everyone={total_everyone} "
            f"total={total_mentions}"
        )

        violated = (
            total_users > self.user_limit or
            total_roles > self.role_limit or
            total_mentions > self.total_limit
        )

        if violated:
            try:
                # bulk delete all tracked messages
                messages_to_delete = [
                    msg for _, msg in dq
                    if not msg.is_system()
                ]

                if len(messages_to_delete) == 1:
                    await messages_to_delete[0].delete()

                elif len(messages_to_delete) > 1:
                    await message.channel.delete_messages(messages_to_delete)

                await message.channel.send(
                    f"{message.author.mention} stop mass mentioning users/roles.",
                )

                # clear cache after punishment
                dq.clear()

            except discord.Forbidden:
                print("Missing permissions: Manage Messages")

            except discord.HTTPException as e:
                print(f"Delete failed: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(AntiMassMention(bot))