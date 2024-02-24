import discord

async def handle_thread_create(thread):
    await thread.fetch_message(thread.id)
    title = thread.name
    content = thread.starter_message.content
    
    