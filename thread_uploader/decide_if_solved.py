# Decision logic if the thread is solved!
# TAGGED SOLVED or ?
from config import (
    FORUM_ID,
    SOLVED_TAG
)

async def handle_tagged(thread):
    if thread.parent_id == FORUM_ID:
        includes_tag = any(tag.name == SOLVED_TAG for tag in thread.applied_tags)

        await thread.fetch_message(thread.id)

        title = thread.name
        content = thread.starter_message.content
        message = title + " " + content
        message_id = thread.starter_message.id