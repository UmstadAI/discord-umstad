import requests
from config import (
    API_ENDPOINT,
    API_KEY,
    FORUM_ID,
    TAG_NAME,
    AUTH_TOKEN,
    LAMBDA_THREAD_PROCESSOR_ENDPOINT,
    format_output,
)


async def handle_thread_create(thread):
    if thread.parent_id == FORUM_ID:
        includes_tag = any(tag.name == TAG_NAME for tag in thread.applied_tags)

        await thread.fetch_message(thread.id)

        title = thread.name
        content = thread.starter_message.content
        message = title + " " + content

        if includes_tag:
            api_response = requests.post(
                API_ENDPOINT,
                json={
                    "message": message,
                    "previewToken": API_KEY,
                    "authToken": AUTH_TOKEN,
                },
            )

            response_content = api_response.content.decode("utf-8")

            await thread.send(format_output(response_content))
        else:
            pass

        lambda_response = requests.post(
            LAMBDA_THREAD_PROCESSOR_ENDPOINT,
            json={
                "thread_id": thread.id,
                "title": title,
                "message": message,
                "created_at": thread.created_at,
                "owner": thread.owner,
            },
        )
