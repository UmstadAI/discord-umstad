import discord
from discord import app_commands
import requests
from config import API_ENDPOINT, API_KEY, COMMAND, COMMAND_PREFIX

async def handle_command(message):
    if message.content.startswith(COMMAND_PREFIX):
        command_body = message.content[len(COMMAND_PREFIX) :].strip()
        command, *args = command_body.split(" ")

        if command == COMMAND:
            api_response = requests.post(
                API_ENDPOINT,
                json={"message": " ".join(args), "previewToken": API_KEY,},
            )

            response_content = api_response.content.decode("utf-8")
            if len(response_content) > 2000:
                response_content = response_content[:2000]

            await message.channel.send(response_content)
