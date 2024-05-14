import requests
from config import (
    FORUM_ID,
    SOLVED_TAG,
    SOLVED_REACTION,
    AUTHORIZED_SOLVED_USERS,
    LAMBDA_THREAD_PROCESSOR_ENDPOINT,
    IS_THREAD_PROCESSOR_DONE,
    GUILD_ID,
)


async def handle_tagged(thread):
    if thread.parent_id == FORUM_ID:
        includes_tag = any(tag.name == SOLVED_TAG for tag in thread.applied_tags)
        if includes_tag:
            message = await thread.fetch_message(thread.id)

            title = thread.name
            content = message.content
            message_content = title + " " + content
            message_id = message.id

            

            return True


async def handle_reacted(thread):
    if thread.parent_id == FORUM_ID:
        message = await thread.fetch_message(thread.id)
        reacted_solved_users = []
        for r in message.reactions:
            if r.emoji == SOLVED_REACTION:
                users = [reacted_solved_users.append(user) async for user in r.users()]

        authorized_solved = any(
            user.id in AUTHORIZED_SOLVED_USERS for user in reacted_solved_users
        )
        print(authorized_solved)
