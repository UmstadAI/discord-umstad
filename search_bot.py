import aiohttp
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


processing_users = set()


@client.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel):
        if message.author == client.user:
            return

        user_id = message.author.id
        if user_id in processing_users:
            await message.channel.send(
                "Please wait until I respond to your previous message."
            )
            return

        processing_users.add(user_id)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    SEARCHER_API_ENDPOINT,
                    json={
                        "message": SEARCHER_MESSAGE_TEMPLATE + message.content,
                        "previewToken": API_KEY,
                        "authToken": AUTH_TOKEN,
                    },
                ) as response:
                    response_content = await response.text()
                    
                    lines = response_content.split('\n')
                    message_buffer = ""
                    
                    for line in lines:
                        if len(message_buffer) + len(line) + 1 > 2000:
                            await message.channel.send(format_output(message_buffer))
                            message_buffer = line + "\n"
                        else:
                            message_buffer += line + "\n"
                    
                    if message_buffer:
                        await message.channel.send(format_output(message_buffer))

        finally:
            processing_users.remove(user_id)


client.run(SEARCHER_DISCORD_TOKEN)
