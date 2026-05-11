import discord
from discord.ext import commands


class AntiMassMention(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.user_limit = 4
        self.role_limit = 3
        self.allow_everyone = False

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        user_mentions = len(message.mentions)
        role_mentions = len(message.role_mentions)
        everyone = 1 if message.mention_everyone else 0

        total_mentions = user_mentions + role_mentions + everyone

        print(
            f"[MENTION CHECK] users={user_mentions} "
            f"roles={role_mentions} everyone={everyone} total={total_mentions}"
        )

        violated = (
            user_mentions > self.user_limit or
            role_mentions > self.role_limit or
            (message.mention_everyone and not self.allow_everyone)
        )

        if violated:
            try:
                await message.delete()

                await message.channel.send(
                    f"{message.author.mention} stop mass mentioning users/roles.",
                    delete_after=5
                )

            except discord.Forbidden:
                print("Missing permissions: Manage Messages")
            except discord.HTTPException as e:
                print(f"Delete failed: {e}")

        await self.bot.process_commands(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(AntiMassMention(bot))