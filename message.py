import aiohttp
import discord
from config import API_ENDPOINT, API_KEY, AUTH_TOKEN, format_output


async def handle_message(message):
    if isinstance(message.channel, discord.DMChannel):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                API_ENDPOINT,
                json={
                    "message": message.content,
                    "previewToken": API_KEY,
                    "authToken": AUTH_TOKEN,
                },
            ) as response:
                response_content = await response.text()

        await message.channel.send(format_output(response_content))
