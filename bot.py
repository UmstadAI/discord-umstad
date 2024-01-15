import discord
import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

intents = discord.Intents.default()
intents.messages = True

client = discord.Client(intents=intents)

endpoint = "https://zkappsumstad.com/api/evalapi/interactions"


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if isinstance(message.channel, discord.DMChannel):
        api_response = requests.post(
            endpoint,
            json={
                "message": message.content,
                "previevToken": os.getenv("OPENAI_API_KEY"),
            },
        )

        print(api_response)
        if api_response.status_code == 200:
            response = api_response
            print(response)
            await message.channel.send(response)



client.run(os.getenv("DISCORD_TOKEN"))
