import discord
import asyncio
import os
import sys
import json
import aiofiles
import logging

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from process_thread import process_thread
from config import (
    DISCORD_TOKEN,
    GUILD_ID,
    FORUM_CHANNEL_ID,
)

from dotenv import load_dotenv

load_dotenv(override=True)

from typing import AsyncIterator

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)

logging.basicConfig(level=logging.INFO)


async def fetch_and_process_threads(channel):
    async for thread in channel.archived_threads(limit=None):
        yield thread


@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user}")

    guild = discord.utils.get(client.guilds, id=GUILD_ID)
    channel = discord.utils.get(client.get_all_channels(), id=FORUM_CHANNEL_ID)

    if guild is None or channel is None:
        logging.error("Guild or Channel not found")
        return

    semaphore = asyncio.Semaphore(10)
    payloads = []

    async def process_and_collect(thread):
        async with semaphore:
            if thread:
                try:
                    payload = await process_thread(thread)
                    payloads.append(payload)
                except Exception as e:
                    logging.error(f"Error processing thread {thread.id}: {e}")

    tasks = [
        process_and_collect(thread)
        async for thread in fetch_and_process_threads(channel)
    ]
    await asyncio.gather(*tasks)

    async with aiofiles.open("payloads.json", "w") as f:
        await f.write(json.dumps(payloads, indent=4))


client.run(DISCORD_TOKEN)
