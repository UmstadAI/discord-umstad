import discord
import requests
from config import API_ENDPOINT, API_KEY, format_output


async def handle_thread_create(thread):
    await thread.fetch_message(thread.id)
    title = thread.name
    content = thread.starter_message.content
    message = title + " " + content

    api_response = requests.post(
        API_ENDPOINT, json={"message": message, "previewToken": API_KEY,},
    )

    response_content = api_response.content.decode("utf-8")

    await thread.send(format_output(response_content))
