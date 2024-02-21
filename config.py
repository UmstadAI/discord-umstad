import os
from dotenv import load_dotenv

load_dotenv(override=True)

COMMAND_PREFIX = "!"
COMMAND = "umstad"
API_ENDPOINT = "https://zkappsumstad.com/api/discord/"
API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1153348653122076673
