# Discord Bot has access a forum channel
# Decide forum thread is answered or solved or closed(How to decide)
# Gets the thread data
# Process the Data (with gpt or not?)
# Upsert it to Vector DB
import sys
import discord
import os 

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
 

from config import DISCORD_TOKEN, GUILD_ID
from dotenv import load_dotenv
from discord import app_commands
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


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    thread = message.channel
    await handle_reacted(thread)
    await handle_tagged(thread)

client.run(DISCORD_TOKEN)