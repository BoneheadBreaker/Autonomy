from discord.ext import commands
import discord
from db import Database

db = Database('bot.db')

db.create_table("test", "text TEXT")
db.create_table("warnings", "user", "reason")

def handle_commands(bot):
    @bot.hybrid_command()
    async def ping(ctx):
        await ctx.send("Pong!")
    
    @bot.hybrid_command(name="documentation", description="display the link for the documentation")
    async def get_documentation(ctx: commands.Context):
        await ctx.send("https://example.com")

    @bot.hybrid_command(name="say", description="talk as the bot!")
    async def say(ctx: commands.Context, text):
        await ctx.channel.send(text)
        if ctx.interaction is None:
            await ctx.message.delete()
        elif ctx.interaction is not None:
                    await ctx.interaction.response.send_message("Sending..", ephemeral=True)
         
    @bot.hybrid_group(name="database", description="edit the database")
    async def database_command(ctx: commands.Context):
         if ctx.invoked_subcommand is None:
              await ctx.send("Invalid use, please pass a valid subcommand")    
                
    @database_command.command(name="add", description="add to an existing table")
    async def database_add_command(ctx: commands.Context, table, data):   
        if data.startswith('"') and data.endswith('"'):
             data = data[1:-1]

        values = [v.strip() for v in data.split(",")]

        db.add(table, *values)
        await ctx.send(f"added {data} to the database")
    
    @database_command.command(name="create", description="create a table")
    async def database_create_command(ctx: commands.Context, table, columns):
         db.create_table(table, columns)    

    @bot.hybrid_group(name="warn", description="warn a user")
    async def warn_command(ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid use, please pass a valid subcommand") 
    
    @warn_command.command(name="add", description="add a warning to a user")
    async def warn_add_command(ctx: commands.Context, user: discord.Member, *, reason: str):
        db.add("warnings", user.id, reason)
        await ctx.send(f"{user.mention} was warned for {reason}")