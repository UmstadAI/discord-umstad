import os
from dotenv import load_dotenv

load_dotenv(override=True)

COMMAND_PREFIX = "!"
COMMAND = "umstad"
API_ENDPOINT = "https://zkappsumstad.com/api/discord/"
SEARCHER_API_ENDPOINT = "https://zkappsumstad.com/api/searcher/"

API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SEARCHER_DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

GUILD_ID = 1153348653122076673
FORUM_ID = 1154341442706231387
TAG_NAME = "qa"

IS_TURBO = False

SEARCHER_MESSAGE_TEMPLATE = """
Search with searcher tool.
"""


def format_output(output):
    if not IS_TURBO:
        if len(output) > 2000:
            output = output[:2000]
    return output
