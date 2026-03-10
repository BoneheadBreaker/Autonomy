import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from commands import handle_commands
from logs import logs
from ConfigLoader import load_config

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

CONFIG = load_config()

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True
intents.messages = True

DEV_GUILD_ID = 1254318703554723901

# Bot class
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=CONFIG["general"]["prefix"],
            intents=intents
        )

    async def setup_hook(self):
        guild = discord.Object(id=DEV_GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

bot = MyBot()

handle_commands(bot)
logs(bot, CONFIG=CONFIG)

# Events
@bot.event
async def on_ready():
    status_type = CONFIG["general"]["status_type"].lower()
    status_text = CONFIG["general"]["status_text"]

    if status_type == "playing":
        activity = discord.Game(name=status_text)

    elif status_type == "watching":
        activity = discord.Activity(type=discord.ActivityType.watching, name=status_text)

    elif status_type == "listening":
        activity = discord.Activity(type=discord.ActivityType.listening, name=status_text)

    else:
        raise ValueError(f"Invalid status_type in config.yml: {status_type}")

    await bot.change_presence(activity=activity, status=discord.Status.online)

    print("Applied presence from config:", status_type, status_text)

@bot.event
async def on_member_join(member: discord.Member):
    channel_id = CONFIG["welcome"]["channel_id"]
    message_template = CONFIG["welcome"]["message"]

    if channel_id:
        print(member.guild)
        channel = member.guild.get_channel(channel_id)
        print("Channel found:", channel)
        if channel:
            await channel.send(message_template.format(user=member.mention))


bot.run(DISCORD_TOKEN)
