import discord
from discord.ext import commands
from db import Database
import re

db = Database('bot.db')

def logs(bot, CONFIG):
    @bot.event
    async def on_message_delete(message):
        if message.guild is None:
            return

        log_channel = get_log_channel(bot, message.guild.id)
        if log_channel is None:
            return

        if CONFIG["logging"]["deleted_messages"]:
            embed = discord.Embed(
                title = "Log - Message deleted",
                description = f"Message Content: {message.system_content}\nAuthor: {message.author}",
                colour = 0xff0000
            )

            await log_channel.send(embed=embed)

    @bot.event
    async def on_message_edit(old_message, new_message):
        if old_message.guild is None:
            return

        if old_message.author == bot.user:
            return

        log_channel = get_log_channel(bot, old_message.guild.id)
        if log_channel is None:
            return

        if CONFIG["logging"]["edited_messages"]:
            old_embed = discord.Embed(
                title="Old Message",
                description=f"{old_message.system_content}\nAuthor: {old_message.author}",
                colour=0xffa500
            )

            new_embed = discord.Embed(
                title="New Message",
                description=f"{new_message.system_content}\nAuthor: {new_message.author}",
                colour=0x00ff00
            )

            await log_channel.send(embed=old_embed)
            await log_channel.send(embed=new_embed)

    @bot.event
    async def on_member_join(member: discord.member):
        guild_id = member.guild.id

        joined_at_timestamp = int(member.joined_at.timestamp())

        log_channel = get_log_channel(bot, guild_id)
        if log_channel is None:
            return

        if CONFIG["logging"]["member_join"]:
            member_join_embed = discord.Embed(
                title = "Log - Member join",
                description = f"Member: {member.mention} their user id is: {member.id} they joined: <t:{joined_at_timestamp}:R>)"
            )

            await log_channel.send(embed=member_join_embed)
    
    @bot.event
    async def on_member_remove(member: discord.member):
        guild_id = member.guild.id

        log_channel = get_log_channel(bot, guild_id)
        if log_channel is None:
            return

        if CONFIG["logging"]["member_remove"]:
            member_remove_embed = discord.Embed(
                title = "Log - Member Leave/Remove",
                description = f"Member: {member.mention} left the server, their user id is: {member.id}",
                colour = 0xff0000
            )

            await log_channel.send(embed=member_remove_embed)

    @bot.event
    async def on_message(message):
        guild_id = message.guild.id

        log_channel = get_log_channel(bot, guild_id)

        if CONFIG["logging"]["invites"]:
            if message.author == bot.user:
                return

            INVITE_REGEX = re.compile(
                r"(?:https?://)?(?:www\.)?"
                r"(?:discord\.gg|discord\.com/invite|discordapp\.com/invite|discordapp\.com)/"
                r"[A-Za-z0-9-]+",
                re.IGNORECASE
            )

            invite_links = re.findall(INVITE_REGEX, message.content)
            if invite_links:
                links_found = len(invite_links)
                invite_detected_embed = discord.Embed(
                    title = "Log - Invite Posted",
                    description = f"{message.author} posted {links_found} discord invites in {message.channel}",
                    colour = 0xFFA500
                )

                await log_channel.send(embed=invite_detected_embed)



    def get_log_channel(bot, guild_id):
        rows = db.get("logging_channel", {"guild_id": guild_id})

        if not rows:
            return None

        channel_id = int(rows[0][1])  # (guild_id, channel_id)
        return bot.get_channel(channel_id)