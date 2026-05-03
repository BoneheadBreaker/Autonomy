from discord.ext import commands
import discord
from db import Database
import random

db = Database('bot.db')

# Tables
db.create_table("test", "guild_id INTEGER", "text TEXT")
db.create_table("warnings", "guild_id INTEGER", "user INTEGER", "reason TEXT")
db.create_table("DB_ACCESS_TOKENS", "TOKENS TEXT")  # global table to store private tokens only handed to trusted people
db.create_table("logging_channel", "guild_id INTEGER", "channel TEXT")

def handle_commands(bot):

    @bot.hybrid_command()
    async def ping(ctx):
        await ctx.send("Pong!")

    @bot.hybrid_command(name="documentation", description="display the link for the documentation")
    async def get_documentation(ctx: commands.Context):
        await ctx.send("https://boneheadbreaker.github.io/Autonomy/")

    @bot.hybrid_command(name="say", description="talk as the bot!")
    @commands.has_permissions(manage_messages=True)
    async def say(ctx: commands.Context, *, text: str):
        if ctx.interaction:
            await ctx.interaction.response.send_message("Sending..", ephemeral=True)
            await ctx.channel.send(text)
        else:
            await ctx.send(text)
            await ctx.message.delete()

    # Database commands
    @bot.hybrid_group(name="database", description="edit the database")
    async def database_command(ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid use, please pass a valid subcommand")

    @database_command.command(name="add", description="add to an existing table")
    async def database_add_command(ctx: commands.Context, token, table, data):

        if not db.exists("DB_ACCESS_TOKENS", "TOKENS", token):
            await ctx.send("Invalid database token.")
            return

        if data.startswith('"') and data.endswith('"'):
            data = data[1:-1]

        values = [v.strip() for v in data.split(",")]

        if table in ["test", "warnings"]:
            db.add(table, ctx.guild.id, *values)
        else:
            db.add(table, *values)

        await ctx.send(f"Added {data} to the database")

    @database_command.command(name="create", description="create a table")
    async def database_create_command(ctx: commands.Context, token, table, columns):

        if not db.exists("DB_ACCESS_TOKENS", "TOKENS", token):
            await ctx.send("Invalid database token.")
            return

        db.create_table(table, columns)
        await ctx.send(f"Table `{table}` created")

    # Warning system
    @bot.hybrid_group(name="warn", description="warn a user")
    async def warn_command(ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid use, please pass a valid subcommand")

    @warn_command.command(name="add", description="add a warning to a user")
    @commands.has_permissions(moderate_members=True)
    async def warn_add_command(ctx: commands.Context, user: discord.Member, *, reason: str):
        db.add("warnings", ctx.guild.id, user.id, reason)
        await ctx.send(f"{user.mention} was warned for {reason}")

    @warn_command.command(name="remove", description="Remove a warning from a user")
    @commands.has_permissions(moderate_members=True)
    async def warn_remove_command(ctx: commands.Context, user: discord.Member):
        db.delete("warnings", {
            "guild_id": ctx.guild.id,
            "user": user.id
        })
        await ctx.send(f"Removed Warnings for {user.mention}")
        
    # config command
    @bot.hybrid_group(name="config", description="Update the config for the bot")
    async def config_command(ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid use, please pass a valid subcommand")
    
    @config_command.command(name="logging_channel", description="set the channel to send logs to")
    @commands.has_permissions(administrator=True)
    async def config_log_channel_command(ctx: commands.Context, channel: discord.TextChannel):
        db.add("logging_channel", ctx.guild.id, channel.id)
        await ctx.send(f"logging channel id set to {channel.id} which is the {channel} channel")

    @bot.hybrid_command(name="ban", description="ban a member")
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
        try:
            await member.ban(reason=reason)
            await ctx.send(f"Banned {member.mention} for {reason}")
        except discord.Forbidden:
            await ctx.send(f"I do not have permission to ban {member}")
        except discord.HTTPException:
            await ctx.send(f"Failed to ban {member}")
        
    @bot.hybrid_command(name="coinflip", description="flip a coin!")
    async def coinflip(ctx):
        coinflip = random.randint(0, 1)
        if coinflip == 1:
            await ctx.send("Heads!")
        else:
            await ctx.send("Tails!")