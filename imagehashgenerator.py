# this script is a tool to be used seperately from Autonomy to find image hashes
# these image hashes can be put in a blocked hashes file to prevent popular scams

import requests
from PIL import Image
import imagehash
from io import BytesIO

def get_image_hash(url):
    # Download the image
    response = requests.get(url)
    response.raise_for_status()

    # Open image
    img = Image.open(BytesIO(response.content))

    # Generate perceptual hash (phash is a good default)
    phash = imagehash.phash(img)

    return phash

if __name__ == "__main__":
    url = input("Enter Discord image URL: ").strip()
    img_hash = get_image_hash(url)

    print(f"Image pHash: {img_hash}")