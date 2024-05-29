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


SLASH_PROMPT = "You see discord chat history, understand the problem and answer it. MAX 1500 Character"


async def handle_slash_command(msg, messages):
    messages.reverse()

    history_str = ""
    for message in messages:
        for username, text in message.items():
            history_str += f"{username}: {text}\n"

    print(history_str)

    ai_request = SLASH_PROMPT + " " + history_str + " " + msg

    api_response = requests.post(
        API_ENDPOINT,
        json={"message": ai_request, "previewToken": API_KEY, "authToken": AUTH_TOKEN,},
    )

    response_content = api_response.content.decode("utf-8")

    return response_content
