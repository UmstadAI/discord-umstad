import discord
import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

intents = discord.Intents.default()
intents.messages = True

client = discord.Client(intents=intents)

endpoint = "https://zkappsumstad.com/api/evalapi/"

api_key=os.getenv("OPENAI_API_KEY")

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
                "previewToken": api_key,
            },
        )

        print(api_response)
        response_content = api_response.content.decode('utf-8')
        if len(response_content) > 2000:
            response_content = response_content[:2000]
        await message.channel.send(response_content)

client.run(os.getenv("DISCORD_TOKEN"))
