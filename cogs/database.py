from discord.ext import commands

from .shared import db, command_enabled


class DatabaseCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(name="database")
    @command_enabled(default=True)
    async def database(self, ctx):

        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid use")

    @database.command(name="add")
    @command_enabled(default=True)
    async def database_add(
        self,
        ctx,
        token,
        table,
        data
    ):

        if not db.exists(
            "DB_ACCESS_TOKENS",
            "TOKENS",
            token
        ):
            await ctx.send("Invalid token")
            return

        if data.startswith('"') and data.endswith('"'):
            data = data[1:-1]

        values = [v.strip() for v in data.split(",")]

        if table in ["test", "warnings"]:
            db.add(table, ctx.guild.id, *values)
        else:
            db.add(table, *values)

        await ctx.send(f"Added {data}")

    @database.command(name="create")
    @command_enabled(default=True)
    async def database_create(
        self,
        ctx,
        token,
        table,
        columns
    ):

        if not db.exists(
            "DB_ACCESS_TOKENS",
            "TOKENS",
            token
        ):
            await ctx.send("Invalid token")
            return

        db.create_table(table, columns)

        await ctx.send(f"Created `{table}`")


async def setup(bot):
    await bot.add_cog(DatabaseCog(bot))