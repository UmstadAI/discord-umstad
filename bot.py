import discord
import os
import requests
from commands import handle_command
from dotenv import load_dotenv
from discord import app_commands

load_dotenv(override=True)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

COMMAND_PREFIX = "!"
COMMAND = "umstad"

client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)

endpoint = "https://zkappsumstad.com/api/evalapi/"

api_key = os.getenv("OPENAI_API_KEY")


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=1153348653122076673))
    print(f"We have logged in as {client.user}")


@tree.command(
    name="umstad",
    description="Call umstad Command",
    guild=discord.Object(id=1153348653122076673),
)
async def on_command(interaction: discord.Interaction):
    await interaction.response.send_message("message")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    await handle_command(message)

    if isinstance(message.channel, discord.DMChannel):
        api_response = requests.post(
            endpoint, json={"message": message.content, "previewToken": api_key,},
        )

        print(api_response)
        response_content = api_response.content.decode("utf-8")

        await message.channel.send(response_content)


client.run(os.getenv("DISCORD_TOKEN"))
