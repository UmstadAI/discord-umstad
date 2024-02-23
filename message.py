import requests
import discord
from discord import app_commands
from config import API_ENDPOINT, API_KEY, COMMAND, COMMAND_PREFIX


async def handle_message(message):
    if isinstance(message.channel, discord.DMChannel):
        api_response = requests.post(
            API_ENDPOINT, json={"message": message.content, "previewToken": API_KEY,},
        )

        response_content = api_response.content.decode("utf-8")

        await message.channel.send(response_content)
