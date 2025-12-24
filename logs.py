import discord
from discord.ext import commands

def logs(bot):
    @bot.event
    async def on_message_delete(message):

        if message.channel is None:
            return

        embed = discord.Embed(title="Log - Message deleted", description=f"Message Content: {message.system_content} Author: {message.author}")

        await message.channel.send(embed=embed)

    @bot.event
    async def on_message_edit(old_message, new_message):
        
        if old_message.channel is None or new_message.channel is None:
            return
        
        if old_message.author == bot.user:
            return

        old_message_embed = discord.Embed(title="Log - Message edited old content", description=f"Old Message Content: {old_message.system_content} Author: {old_message.author}")

        new_message_embed = discord.Embed(title="Log - Message edited new content", description=f"New Message Content: {new_message.system_content} Author: {new_message.author}")

        await old_message.channel.send(embed=old_message_embed)
        await new_message.channel.send(embed=new_message_embed)
