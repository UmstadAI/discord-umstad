import discord
import os
import requests
from dotenv import load_dotenv
from discord import app_commands

load_dotenv(override=True)

intents = discord.Intents.default()
intents.messages = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

endpoint = "https://zkappsumstad.com/api/evalapi/"

api_key=os.getenv("OPENAI_API_KEY")

COMMAND_PREFIX = "!"
COMMAND = "umstad"

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=1153348653122076673))
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith(COMMAND_PREFIX):
        command_body = message.content[len(COMMAND_PREFIX):].strip()
        command, *args = command_body.split(' ')

        print(command)

        if command == COMMAND:
            await message.channel.send("You triggered a command!")

@tree.command(
    name="umstad",
    description="Call umstad Command",
    guild=discord.Object(id=1153348653122076673)
)
async def on_command(interaction: discord.Interaction):
    await interaction.response.send_message("message")


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

        # If it is turbo discord etc. remove if :D
        if len(response_content) > 2000:
            response_content = response_content[:2000]
        await message.channel.send(response_content)

client.run(os.getenv("DISCORD_TOKEN"))