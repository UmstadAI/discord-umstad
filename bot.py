import discord
from config import DISCORD_TOKEN, GUILD_ID
from search_bot import handle_search
from commands import handle_command
from message import handle_message
from forum_listener import handle_thread_create
from dotenv import load_dotenv
from discord import app_commands

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


@tree.command(
    name="umstad", description="Call umstad Command", guild=discord.Object(id=GUILD_ID),
)
async def on_command(interaction: discord.Interaction):
    # TODO!
    await interaction.response.send_message("message")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    await handle_command(message)
    await handle_message(message)


@client.event
async def on_thread_create(thread):
    await handle_thread_create(thread)


client.run(DISCORD_TOKEN)
