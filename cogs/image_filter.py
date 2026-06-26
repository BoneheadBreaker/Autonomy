import discord
from discord.ext import commands

import imagehash
from PIL import Image, ImageFile

import requests

from io import BytesIO
import httpx
import sys, site

print("EXEC:", sys.executable)
print("VERSION:", sys.version)
print("SITE:", site.getsitepackages())
print("PATH:")
for p in sys.path:
    print(" ", p)

ImageFile.LOAD_TRUNCATED_IMAGES = True


class ImageFilterCog(commands.Cog):
    def __init__(self, bot, hash_file="./threat_database/scam_hashes.txt", threshold=5):
        self.bot = bot
        self.hash_file = hash_file
        self.threshold = threshold

        self.known_hashes = self.load_hashes()

    def load_hashes(self):
        hashes = []

        try:
            with open(self.hash_file, "r") as f:
                for line in f:
                    line = line.strip()

                    if not line:
                        continue

                    try:
                        hashes.append(
                            imagehash.hex_to_hash(line)
                        )

                    except Exception as e:
                        print(
                            f"[ImageFilter] Invalid hash skipped: "
                            f"{line} ({e})"
                        )

            print(f"[ImageFilter] Loaded {len(hashes)} hashes")

        except FileNotFoundError:
            print(
                f"[ImageFilter] Hash file not found: "
                f"{self.hash_file}"
            )

        return hashes


    def extract_urls(self, message):
        urls = []

        # Attachments
        for attachment in message.attachments:
            if (
                attachment.content_type
                and "image" in attachment.content_type
            ):
                urls.append(attachment.url)

        # Embeds
        for embed in message.embeds:
            if embed.image and embed.image.url:
                urls.append(embed.image.url)

            if embed.thumbnail and embed.thumbnail.url:
                urls.append(embed.thumbnail.url)

        return urls

    def check_url(self, url):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            img = Image.open(BytesIO(response.content))

            phash = imagehash.phash(img)

            for known in self.known_hashes:
                distance = phash - known

                if distance <= self.threshold:
                    return True, distance

        except Exception as e:
            print(f"[ImageFilter] Error: {e}")

        return False, None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None:
            return

        if message.author.bot:
            return

        urls = self.extract_urls(message)

        if not urls:
            return

        for url in urls:
            match, distance = self.check_url(url)

            if match:
                try:
                    await message.delete()

                    print(f"[ImageFilter] Deleted (distance={distance})")

                    logs_cog = self.bot.get_cog("LogsManager")

                    if logs_cog:
                        await logs_cog.add_log(
                            guild_id = message.guild.id,
                            event_name = "Log - Known scam image",
                            event_description=(
                                f"Author: {message.author} ({message.author.id})\n"
                                f"Channel: {message.channel.mention}\n"
                                f"Distance: {distance}\n"
                                f"Message Content: {message.content or 'message contained no text'}"
                            ),
                            event_colour=0xff0000
                        )

                except discord.Forbidden:
                    await logs_cog.add_log(
                        guild_id = message.guild.id,
                        event_name = "Log - Known scam image",
                        event_description=(
                            f"Author: {message.author} ({message.author.id})\n"
                            f"Channel: {message.channel.mention}\n"
                            f"Distance: {distance}\n"
                            f"Message Content: {message.content or 'message contained no text'}"
                            "WARNING"
                            "Autonomy LACKED THE PERMISSIONS TO DELETE THE MESSAGE"
                        )
                    )

                except Exception as e:
                    print(f"[ImageFilter] Delete failed: {e}")

                return

            else:
                # Use modapi.xyz to check it
                print(self.bot.mod_api_token)
                headers = {
                    "Authorization": f"Bearer {self.bot.mod_api_token}"
                }

                try:
                    async with httpx.AsyncClient(timeout=15) as client:
                        # Download the image into RAM
                        image = await client.get(url)
                        image.raise_for_status()

                        # Send it to ModAPI
                        response = await client.post(
                            "https://api.modapi.xyz/v1/moderate/image/scam",
                            headers=headers,
                            files={
                                "file": (
                                    "image.png",
                                    image.content,
                                    image.headers.get("Content-Type", "application/octet-stream"),
                                )
                            },
                        )

                        response.raise_for_status()
                        result = response.json()

                    print(result)

                    # Delete the message if ModAPI flagged it
                    if result.get("flagged", False):
                        await message.delete()
                        print("[ImageFilter] Deleted (ModAPI flagged image)")

                        return

                except discord.Forbidden:
                    print("[ImageFilter] Missing permission to delete the message.")

                except httpx.HTTPError as e:
                    print(f"[ImageFilter] ModAPI request failed: {e}")

                except Exception as e:
                    print(f"[ImageFilter] Unexpected error: {e}")
            

async def setup(bot):
    await bot.add_cog(
        ImageFilterCog(
            bot,
            hash_file="./threat_database/scam_hashes.txt",
            threshold=5
        )
    )