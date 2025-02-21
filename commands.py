import logging
import aiohttp
from typing import List, Dict
from config import (
    API_ENDPOINT,
    API_KEY,
    COMMAND,
    COMMAND_PREFIX,
    AUTH_TOKEN,
    format_output,
)

logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self, endpoint: str, api_key: str, auth_token: str):
        self.endpoint = endpoint
        self.api_key = api_key
        self.auth_token = auth_token
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def send_request(self, message: str) -> str:
        try:
            async with self.session.post(
                self.endpoint,
                json={
                    "message": message,
                    "previewToken": self.api_key,
                    "authToken": self.auth_token,
                },
                timeout=30,  # Add timeout
            ) as response:
                if response.status != 200:
                    logger.error(f"API request failed with status {response.status}")
                    return "Sorry, I encountered an error processing your request."
                return await response.text()
        except aiohttp.ClientError as e:
            logger.error(f"API request failed: {e}")
            return "Sorry, I'm having trouble connecting to the server."
        except Exception as e:
            logger.error(f"Unexpected error during API request: {e}")
            return "An unexpected error occurred."


async def handle_command(message):
    try:
        if not message.content.startswith(COMMAND_PREFIX):
            return

        command_body = message.content[len(COMMAND_PREFIX) :].strip()
        command, *args = command_body.split(" ")

        if command != COMMAND:
            return

        async with APIClient(API_ENDPOINT, API_KEY, AUTH_TOKEN) as api_client:
            response_content = await api_client.send_request(" ".join(args))
            formatted_response = format_output(response_content)
            await message.channel.send(formatted_response)

    except Exception as e:
        logger.error(f"Error handling command: {e}")
        await message.channel.send(
            "Sorry, something went wrong while processing your command."
        )


SLASH_PROMPT = "You see discord chat history, understand the problem and answer it. MAX 1500 Character"


async def handle_slash_command(msg: str, messages: List[Dict[str, str]]) -> str:
    try:
        messages.reverse()
        history_str = ""
        for message in messages:
            for username, text in message.items():
                history_str += f"{username}: {text}\n"

        logger.debug(f"Processing message history: {history_str}")

        ai_request = f"{SLASH_PROMPT} {history_str} {msg}"

        async with APIClient(API_ENDPOINT, API_KEY, AUTH_TOKEN) as api_client:
            response_content = await api_client.send_request(ai_request)
            return response_content

    except Exception as e:
        logger.error(f"Error handling slash command: {e}")
        return "Sorry, something went wrong while processing your command."
