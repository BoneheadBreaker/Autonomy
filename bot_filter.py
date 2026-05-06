import imagehash
from PIL import Image, ImageFile
import requests
from io import BytesIO

ImageFile.LOAD_TRUNCATED_IMAGES = True

class ImageFilter:
    def __init__(self, hash_file, threshold=5):
        self.hash_file = hash_file
        self.threshold = threshold
        self.known_hashes = self.load_hashes()

    def load_hashes(self):
        hashes = []
        with open(self.hash_file, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        hashes.append(imagehash.hex_to_hash(line))
                    except Exception as e:
                        print(f"[ImageFilter] Invalid hash skipped: {line} ({e})")
        print(f"[ImageFilter] Loaded {len(hashes)} hashes")
        return hashes

    def extract_urls(self, message):
        urls = []

        # Attachments
        for attachment in message.attachments:
            if attachment.content_type and "image" in attachment.content_type:
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