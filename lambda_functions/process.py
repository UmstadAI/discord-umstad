# Processor with OPENAI
# DATA FORMAT WILL BE:
# THREAD ID, THREAD OWNER, THREAD TITLE, THREAD MESSAGES
# Example Thread Link: https://discord.com/channels/1153348653122076673/1213075628748709898
# Guild ID + Thread ID
# Example Message Link: https://discord.com/channels/1153348653122076673/1213072868175384587/1213084598603354172
# Guild ID + Thread ID + Message ID

import json
import glob
import os
from openai import OpenAI
import time
import re

from pinecone import Pinecone, ServerlessSpec
from datetime import datetime
from dateutil import parser

from uuid import uuid4
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv(), override=True)  # read local .env file

pinecone_api_key = os.getenv("PINECONE_API_KEY") or "YOUR_API_KEY"
pinecone_env = os.getenv("PINECONE_ENVIRONMENT") or "YOUR_ENV"
openai_api_key = os.getenv("OPENAI_API_KEY")


def lambda_handler(event, context=None):
    DEMO_UNANSWERED_VECTOR_TYPE = "demo-search-unanswered"
    UNANSWERED_VECTOR_TYPE = "search-unanswered"
    IS_DEMO = True

    guild_id = event.get("guild_id")
    thread_id = event.get("thread_id")
    title = event.get("title")
    message = event.get("message")
    message_id = event.get("message_id")
    created_at = event.get("created_at")
    owner_id = event.get("owner_id")

    # Process DATA and upload
    date_object = parser.parse(created_at)
    created_at = date_object.timestamp()

    thread_link = f"https://discord.com/channels/{guild_id}/{thread_id}"
    message_link = f"{thread_link}/{message_id}"

    # LOG THE THREAD DATA
    print("Guild ID: ", guild_id)
    print("Thread ID:", thread_id)
    print("Title: ", title)
    print("Message: ", message)
    print("Message ID: ", message_id)
    print("Created AT: ", created_at)
    print("Owner: ", owner_id)

    client = OpenAI(api_key=openai_api_key)
    pc = Pinecone(api_key=pinecone_api_key)

    index_name = "zkappumstad"
    model_name = "text-embedding-3-small"

    index = pc.Index(index_name)

    if IS_DEMO:
        vector_type = DEMO_UNANSWERED_VECTOR_TYPE
    else:
        vector_type = UNANSWERED_VECTOR_TYPE

    vector_id = str(uuid4())
    embedding_response = client.embeddings.create(
        input= title + " " + message,
        model="text-embedding-3-small"
    )

    embedding = embedding_response.data[0].embedding

    metadata = {
        "vector_type": vector_type,
        "guild_id": guild_id,
        "thread_id": thread_id,
        "title": title,
        "message": message,
        "message_id": message_id,
        "created_at": created_at,
        "owner_id": owner_id,
        "thread_link": thread_link,
        "message_link": message_link,
    }

    vector = {
        "id": vector_id,
        "values": embedding,
        "metadata": metadata
    }

    response = index.upsert(
        vectors = [vector]
    )

    print(response)
    return {"statusCode": 200, "body": json.dumps(response)}
