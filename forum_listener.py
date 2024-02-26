import requests
from config import API_ENDPOINT, API_KEY, FORUM_ID, TAG_NAME, format_output
from searcher_api.api import log


async def handle_thread_create(thread):
    if thread.parent_id == FORUM_ID:
        includes_qa_tag = any(tag.name == TAG_NAME for tag in thread.applied_tags)
        if includes_qa_tag:
            await thread.fetch_message(thread.id)
            title = thread.name
            content = thread.starter_message.content
            message = title + " " + content

            api_response = requests.post(
                API_ENDPOINT, json={"message": message, "previewToken": API_KEY,},
            )

            response_content = api_response.content.decode("utf-8")

            await thread.send(format_output(response_content))
        else:
            pass

        # TODO GET AND SEND THREAD TO THE PREPROCESSED DB FOR SEARCHER BOT FOR PROCESSING
        log(message)

