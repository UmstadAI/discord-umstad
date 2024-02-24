import discord

async def handle_thread_create(thread):
    print(thread.name)
    print(thread.last_message)