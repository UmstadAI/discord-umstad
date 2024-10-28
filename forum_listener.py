import aiohttp
import os
import discord
from discord import app_commands
from openai import OpenAI
from pinecone import Pinecone

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

pinecone_api_key = os.getenv("PINECONE_API_KEY") or "YOUR_API_KEY"
pinecone_env = os.getenv("PINECONE_ENVIRONMENT") or "YOUR_ENV"

openai = OpenAI(api_key=API_KEY)
pc = Pinecone(api_key=pinecone_api_key)

index_name = "zkappumstad"
model_name = "text-embedding-3-small"

index = pc.Index(index_name)
SCORE = 0.25


async def handle_thread_create(thread):
    if thread.parent_id == FORUM_ID:
        includes_tag = any(tag.name == TAG_NAME for tag in thread.applied_tags)
        try:
            await thread.fetch_message(thread.id)

            title = thread.name
            content = thread.starter_message.content
            message = title + " " + content
            message_id = thread.starter_message.id

            if includes_tag:
                res = openai.embeddings.create(input=[message], model=model_name)

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
                        message_id = (
                            metadata.get("message_id")
                            if metadata.get("message_id")
                            else None
                        )
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
                        await thread.send(message_buffer)
                        message_buffer = line
                    else:
                        message_buffer += line

                if message_buffer:
                    await thread.send(message_buffer)
        except Exception as e:
            print(e)
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
