# TODO!: Process thread with all messages and ids etc.
# TODO!: Add API to main.py for also processed threads

from config import (
    FORUM_ID,
    GUILD_ID,
)


async def process_thread(thread):
    print("Processing: ", thread)

    # Return it

    guild_id = int(GUILD_ID)
    thread_id = int(thread.id),
    title = str(thread.name)
    messages = []
    created_at = str(thread.created_at)
    owner_id = str(thread.owner_id)

    async for message in thread.history(limit=100):
        message_id = message.id
        content = message.content
        author = message.author.name

        message = {
            "Message ID": message_id,
            "Author": author,
            "Message Content": content
        }

        messages.append(message)

    messages.reverse()
    
    formatted_messages = "\n".join(
        f"Message ID: {msg['Message ID']}, Author: {msg['Author']}, Message: {msg['Message Content']}" 
        for msg in messages
    )

    payload_thread = {
        "guild_id": guild_id,
        "thread_id": thread_id,
        "title": title,
        "messages": messages,
        "created_at": created_at,
        "owner_id": owner_id,
    }

    print(payload_thread)


