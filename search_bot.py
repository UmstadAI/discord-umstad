import os
import aiohttp
import discord
from discord import app_commands
from openai import OpenAI
from pinecone import Pinecone

from config import (
    SEARCHER_API_ENDPOINT,
    API_KEY,
    SEARCHER_MESSAGE_TEMPLATE,
    SEARCHER_DISCORD_TOKEN,
    AUTH_TOKEN,
    GUILD_ID,
    format_output,
)

pinecone_api_key = os.getenv("PINECONE_API_KEY") or "YOUR_API_KEY"
pinecone_env = os.getenv("PINECONE_ENVIRONMENT") or "YOUR_ENV"

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

openai = OpenAI(api_key=API_KEY)
pc = Pinecone(api_key=pinecone_api_key)

index_name = "zkappumstad"
model_name = "text-embedding-3-small"

index = pc.Index(index_name)


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"We have logged in as searcher bot {client.user}")


processing_users = set()

SCORE = 0.25


@client.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel):
        if message.author == client.user:
            return

        user_id = message.author.id
        if user_id in processing_users:
            await message.channel.send(
                "Please wait until I respond to your previous message."
            )
            return

        processing_users.add(user_id)

        try:
            message_text = message.content
            res = openai.embeddings.create(input=[message_text], model=model_name)

            embedding_res = res.data[0].embedding

            response = index.query(
                vector=embedding_res,
                top_k=5,
                filter={"vector_type": {"$eq": "demo-search"},},
                include_values=True,
                include_metadata=True,
            )

            results = []
            for i, match in enumerate(response.matches, 1):
                if (match.score or 1) > SCORE:
                    metadata = match.metadata
                    title = metadata.get("title")
                    message_id = metadata.get("message_id") if metadata.get("message_id") else None
                    thread_link = metadata.get("thread_link")
                    message_link = metadata.get("message_link")

                    result = f"**{i}. {title}**\n"
                    result += f"◦ **Thread Link:** ({thread_link})"
                    if message_id != None:
                        result += f"\n◦ **Message Link:** ({message_link})"
                    results.append(result)

            print(results)
            message_buffer = ""

            for result in results:
                line = result + "\n\n"
                if len(message_buffer) + len(line) > 2000:
                    await message.channel.send(message_buffer)
                    message_buffer = line
                else:
                    message_buffer += line

            if message_buffer:
                await message.channel.send(message_buffer)
        finally:
            processing_users.remove(user_id)


client.run(SEARCHER_DISCORD_TOKEN)
