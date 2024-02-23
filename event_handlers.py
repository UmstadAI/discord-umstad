import discord
from discord import app_commands
from commands import handle_command


async def on_ready(client, tree, guild_id):
    await tree.sync(guild=discord.Object(id=guild_id))
    print(f"We have logged in as {client.user}")


async def on_message(message, client):
    if message.author == client.user:
        return

    await handle_command(message)


def setup_event_handlers(client, tree):
    client.event(lambda: on_ready(client, tree, guild_id=1153348653122076673))
    client.event(lambda message: on_message(message, client))
