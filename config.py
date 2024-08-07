import os
from dotenv import load_dotenv

load_dotenv(override=True)

COMMAND_PREFIX = "!"
COMMAND = "umstad"
API_ENDPOINT = "https://zkappsumstad.com/api/discord/"
SEARCHER_API_ENDPOINT = "https://zkappsumstad.com/api/demosearch/"
LAMBDA_THREAD_PROCESSOR_ENDPOINT = "http://127.0.0.1:8000/"

API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SEARCHER_DISCORD_TOKEN = os.getenv("SEARCHER_DISCORD_TOKEN")
THERAD_UPLOADER_DISCORD_TOKEN = os.getenv("THREAD_UPLOADER_DISCORD_TOKEN")

AUTH_TOKEN = os.getenv("AUTH_TOKEN")
FORUM_CHANNEL_ID = 1154341442706231387

DEMO_VECTOR_TYPE = "demo-search"
VECTOR_TYPE = "search"

GUILD_ID = 1153348653122076673
FORUM_ID = 1154341442706231387
TAG_NAME = "AI Support"

SOLVED_TAG = "Solved"
SOLVED_REACTION = "✅"
AUTHORIZED_SOLVED_USERS = [843590451348111420]

IS_TURBO = False
IS_DEMO = True

IS_THREAD_PROCESSOR_DONE = True

SEARCHER_MESSAGE_TEMPLATE = """
Search with demo searcher tool.
If you can't fetch data from demo search tool. Please do not send unrelated content.
Your message must not contain more than 1500 Character.
"""


def format_output(output):
    if not IS_TURBO:
        if len(output) > 2000:
            output = output[:2000]
    return output
