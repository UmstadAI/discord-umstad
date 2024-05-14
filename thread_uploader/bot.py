# Discord Bot has access a forum channel
# We will have already solved and archived threads, so this bot.py necessary only for recent threads

# Decide forum thread is answered or solved with tag: decide_if_solved.py
## We have tiny DB to store solved forum threads to prevent duplicates
## Get Active threads once a day, If active thread solved and not in the TinyDB:
### https://schedule.readthedocs.io/en/stable/
### SEND to Lambda API toProcess and Upsert it via Lambda Functions

## EXTRA: Process with gpt in other worker, and upsert into issue vector


# Gets the thread data
# Process the Data (not with gpt): Create actual processor also in lambda_functions
# Upsert it to Vector DB

import sys
import discord
import os
import time

from tinydb import TinyDB, Query

db = TinyDB("db.json")

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


from config import DISCORD_TOKEN, GUILD_ID, FORUM_ID
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands, tasks
from decide_if_solved import handle_tagged, handle_reacted

load_dotenv(override=True)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True


client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"We have logged in as {client.user}")
    scan.start()


# Change it to 24 hours :)
@tasks.loop(seconds=5)
async def scan():
    guild = discord.utils.get(client.guilds, id=GUILD_ID)
    channel = discord.utils.get(guild.channels, id=FORUM_ID)

    query = Query()
    threads = await guild.active_threads()

    stored_thread_ids = [item["id"] for item in db.all()]
    filtered_threads = [
        thread
        for thread in threads
        if thread.parent_id == channel.id and thread.id not in stored_thread_ids
    ]

    for thread in filtered_threads:
        posted = await handle_tagged(thread)
        if posted:
            db.insert({"id": thread.id})
            print("Inserted", thread.id)




@client.event
async def on_message(message):
    if message.author == client.user:
        return


client.run(DISCORD_TOKEN)
