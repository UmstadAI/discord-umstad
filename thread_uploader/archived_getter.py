#  Get threads
# Process with process_thread
# Upsert them with batches.

import discord
import asyncio
import os
import sys
import json

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


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    guild = discord.utils.get(client.guilds, id=GUILD_ID)
    channel = discord.utils.get(client.get_all_channels(), id=FORUM_CHANNEL_ID)

    if guild is None or channel is None:
        print("Guild or Channel not found")
        return

    channel_threads: AsyncIterator = channel.archived_threads(limit=None)
    archived_threads: list[discord.Thread] = [t async for t in channel_threads]

    payloads = []

    for counter, thread in enumerate(archived_threads):
        if thread:
            payload = await process_thread(thread)
            payloads.append(payload)

    with open("payloads.json", "w") as f:
        json.dump(payloads, f, indent=4)


client.run(DISCORD_TOKEN)
