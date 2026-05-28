from discord.ext import commands
import discord

from .shared import (
    db,
    get_toggleable_commands
)


class ConfigCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if isinstance(error, commands.CheckFailure):

            if ctx.guild:
                await ctx.send(
                    "This command is disabled in this server."
                )

    async def _config_enable(self, ctx, command_name: str):
        valid = get_toggleable_commands(ctx.bot)

        if command_name not in valid:
            return "invalid_command_name"

        command_obj = ctx.bot.get_command(command_name)

        default = True

        if (command_obj and hasattr(command_obj.callback, "__command_default__")):

            default = command_obj.callback.__command_default__

        db.delete(
            "commands_is_enabled",
            {
                "guild_id": ctx.guild.id,
                "command": command_name
            }
        )

        if not default:
            db.add(
                "commands_is_enabled",
                ctx.guild.id,
                command_name,
                True
            )

    async def _config_disable(self, ctx, command_name: str):

        valid = get_toggleable_commands(ctx.bot)

        if command_name not in valid:
            return "invalid_command_name"

        command_obj = ctx.bot.get_command(command_name)

        default = True

        if (
            command_obj and
            hasattr(command_obj.callback, "__command_default__")
        ):
            default = command_obj.callback.__command_default__

        db.delete(
            "commands_is_enabled",
            {
                "guild_id": ctx.guild.id,
                "command": command_name
            }
        )

        if default:
            db.add(
                "commands_is_enabled",
                ctx.guild.id,
                command_name,
                False
            )

    @commands.hybrid_group(name="config")
    async def config(self, ctx):

        if ctx.invoked_subcommand is None:
            await ctx.send("You must use a subcommand")

    @config.command(name="enable")
    @commands.has_permissions(administrator=True)
    async def config_enable(self, ctx, command_name: str):

        error = await self._config_enable(ctx, command_name)

        if error == "invalid_command_name":
            valid_commands = get_toggleable_commands(ctx.bot)

            await ctx.send(
                f"Invalid command. Need help? use /discord to get an invite link for help!\n"
                f"Available commands: {', '.join(valid_commands)}"
            )
        else:
            await ctx.send(f"Enabled `{command_name}`")

    @config.command(name="disable")
    @commands.has_permissions(administrator=True)
    async def config_disable(self, ctx, command_name: str):

        error = await self._config_disable(ctx, command_name)

        if error == "invalid_command_name":
            valid_commands = get_toggleable_commands(ctx.bot)

            await ctx.send(
                f"Invalid command. Need help? use /discord to get an invite link for help!\n"
                f"Available commands: {', '.join(valid_commands)}"
            )
        else:
            await ctx.send(f"Disabled `{command_name}`")

    @config.command(name="list")
    @commands.has_permissions(administrator=True)
    async def config_list(self, ctx):

        cmds = get_toggleable_commands(ctx.bot)

        rows = db.get(
            "commands_is_enabled",
            {"guild_id": ctx.guild.id}
        ) or []

        overrides = {
            row[1]: bool(row[2])
            for row in rows
        }

        lines = []

        for cmd in cmds:

            command_obj = ctx.bot.get_command(cmd)

            default = True

            if (
                command_obj and
                hasattr(
                    command_obj.callback,
                    "__command_default__"
                )
            ):
                default = command_obj.callback.__command_default__

            if cmd in overrides:
                state = (
                    "Enabled"
                    if overrides[cmd]
                    else "Disabled"
                )
            else:
                state = (
                    "Enabled (default)"
                    if default
                    else "Disabled (default)"
                )

            lines.append(f"{cmd}: {state}")

        message = (
            "\n".join(lines)
            if lines
            else "No commands found"
        )

        await ctx.send(f"```\n{message}\n```")

    @config.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def config_reset(self, ctx):

        db.delete(
            "commands_is_enabled",
            {"guild_id": ctx.guild.id}
        )

        await ctx.send(
            "Config as reset back to default"
        )

    @config_enable.autocomplete("command_name")
    @config_disable.autocomplete("command_name")
    async def command_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ):

        cmds = get_toggleable_commands(
            interaction.client
        )

        return [
            discord.app_commands.Choice(
                name=cmd,
                value=cmd
            )
            for cmd in cmds
            if current.lower() in cmd.lower()
        ][:25]


async def setup(bot):
    await bot.add_cog(ConfigCog(bot))