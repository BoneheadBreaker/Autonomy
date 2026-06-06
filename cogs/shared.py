from discord.ext import commands
from db import Database
from datetime import datetime
from pathlib import Path
import os

DB_PATH = os.getenv("DB_PATH", "bot.db")

db = Database(DB_PATH)

db.create_table("test", "guild_id INTEGER", "text TEXT")

db.create_table("warnings", "guild_id INTEGER", "user INTEGER", "reason TEXT")

db.create_table("DB_ACCESS_TOKENS", "TOKENS TEXT")

db.create_table("logging_channel", "guild_id INTEGER", "channel TEXT")

db.create_table("blocked_links", "guild_id INTEGER", "link TEXT")

db.create_table("blocked_words", "guild_id INTEGER", "word TEXT")

db.create_table(
    "modules_is_enabled",
    "guild_id INTEGER",
    "module TEXT",
    "is_enabled BOOLEAN"
)

db.create_table(
    "quarantined_users",
    "guild_id INTEGER",
    "user_id INTEGER",
    "roles TEXT"
)

CUSTOM_MODULES = [
    "logs",
    "logs.deleted_messages",
    "logs.edited_messages",
    "logs.member_join",
    "logs.member_remove",
    "logs.invites"
]

def command_enabled(default=True):

    def decorator(func):

        func.__command_enabled__ = True
        func.__command_default__ = default

        async def predicate(ctx: commands.Context):

            if ctx.guild is None:
                return True

            command = ctx.command
            guild_id = ctx.guild.id

            names_to_check = []

            while command:
                names_to_check.append(command.qualified_name)
                command = command.parent

            for name in names_to_check:

                result = db.get(
                    "modules_is_enabled",
                    {
                        "guild_id": guild_id,
                        "module": name
                    }
                )

                if result:
                    return bool(result[0][2])

            return getattr(
                ctx.command.callback,
                "__command_default__",
                True
            )

        return commands.check(predicate)(func)

    return decorator

def get_toggleable_commands(bot):

    cmds = set()

    for cmd in bot.walk_commands():

        if hasattr(cmd.callback, "__command_enabled__"):

            cmds.add(cmd.qualified_name)

            parent = cmd.parent

            while parent:
                cmds.add(parent.qualified_name)
                parent = parent.parent

    cmds.update(CUSTOM_MODULES)

    return sorted(cmds)

LOG_PATH = os.getenv("LOG_PATH", "./logs")


def log(message: str, level: str = "INFO"):

    try:
        log_file = Path(LOG_PATH)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] [{level}] {message}\n"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(line)

    except Exception as e:
        # fallback so logging never crashes the bot
        print(f"Logging failed: {e}")