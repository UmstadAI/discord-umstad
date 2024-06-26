from config import GUILD_ID


async def process_thread(thread):
    guild_id = str(GUILD_ID)
    thread_id = str(thread.id)
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
            "Message Content": content,
        }

        messages.append(message)

    messages.reverse()

    formatted_messages = "\n ".join(
        f"Message ID: {msg['Message ID']}, Author: {msg['Author']}, Message: {msg['Message Content']}"
        for msg in messages
    )

    payload_thread = {
        "guild_id": guild_id,
        "thread_id": thread_id,
        "title": title,
        "messages": formatted_messages,
        "created_at": created_at,
        "owner_id": owner_id,
    }

    print(payload_thread)
    return payload_thread
