import aiohttp
from config import (
    API_ENDPOINT,
    API_KEY,
    FORUM_ID,
    TAG_NAME,
    AUTH_TOKEN,
    GUILD_ID,
    LAMBDA_THREAD_PROCESSOR_ENDPOINT,
    IS_THREAD_PROCESSOR_DONE,
    format_output,
)


async def handle_thread_create(thread):
    if thread.parent_id == FORUM_ID:
        includes_tag = any(tag.name == TAG_NAME for tag in thread.applied_tags)

        await thread.fetch_message(thread.id)

        title = thread.name
        content = thread.starter_message.content
        message = title + " " + content
        message_id = thread.starter_message.id

        if includes_tag:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    API_ENDPOINT,
                    json={
                        "message": message,
                        "previewToken": API_KEY,
                        "authToken": AUTH_TOKEN,
                    },
                ) as response:
                    response_content = await response.text()

            await thread.send(format_output(response_content))
        else:
            pass

        payload = {
            "guild_id": str(GUILD_ID),
            "thread_id": str(thread.id),
            "title": str(title),
            "message": message,
            "message_id": str(message_id),
            "created_at": str(thread.created_at),
            "owner_id": str(thread.owner_id),
        }

        if IS_THREAD_PROCESSOR_DONE:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    LAMBDA_THREAD_PROCESSOR_ENDPOINT, json=payload
                ) as lambda_response:
                    lambda_response_content = await lambda_response.text()
