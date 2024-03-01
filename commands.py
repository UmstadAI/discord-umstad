import requests
from config import (
    API_ENDPOINT,
    API_KEY,
    COMMAND,
    COMMAND_PREFIX,
    AUTH_TOKEN,
    format_output,
)


async def handle_command(message):
    if message.content.startswith(COMMAND_PREFIX):
        command_body = message.content[len(COMMAND_PREFIX) :].strip()
        command, *args = command_body.split(" ")

        if command == COMMAND:
            api_response = requests.post(
                API_ENDPOINT,
                json={
                    "message": " ".join(args),
                    "previewToken": API_KEY,
                    "authToken": AUTH_TOKEN,
                },
            )

            response_content = api_response.content.decode("utf-8")

            await message.channel.send(format_output(response_content))
