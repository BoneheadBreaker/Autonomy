import discord
import yaml
from pathlib import Path

def load_config():
    ROOT_DIR = Path(__file__).parent
    CONFIG_PATH = ROOT_DIR / "config" / "config.yml"

    with open(CONFIG_PATH, "r") as f:
        CONFIG = yaml.safe_load(f)

    print("Loaded config:", CONFIG)

    return CONFIG