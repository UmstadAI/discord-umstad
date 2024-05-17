import requests
import discord
from discord import app_commands

from config import (
    SEARCHER_API_ENDPOINT,
    API_KEY,
    SEARCHER_MESSAGE_TEMPLATE,
    SEARCHER_DISCORD_TOKEN,
    AUTH_TOKEN,
    GUILD_ID,
    format_output,
)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True


client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"We have logged in as searcher bot {client.user}")


@client.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel):
        if message.author == client.user:
            return
        api_response = requests.post(
            SEARCHER_API_ENDPOINT,
            json={
                "message": SEARCHER_MESSAGE_TEMPLATE + message.content,
                "previewToken": API_KEY,
                "authToken": AUTH_TOKEN,
            },
        )

        response_content = api_response.content.decode("utf-8")
        await message.channel.send(format_output(response_content))


client.run(SEARCHER_DISCORD_TOKEN)
