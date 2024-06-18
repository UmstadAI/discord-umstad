# Example Thread Link: https://discord.com/channels/1153348653122076673/1213075628748709898
# Guild ID + Thread ID
# Example Message Link: https://discord.com/channels/1153348653122076673/1213072868175384587/1213084598603354172
# Guild ID + Thread ID + Message ID

import json
import os
from openai import OpenAI

from pinecone import Pinecone
from dateutil import parser

from uuid import uuid4
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv(), override=True)  # read local .env file

pinecone_api_key = os.getenv("PINECONE_API_KEY") or "YOUR_API_KEY"
pinecone_env = os.getenv("PINECONE_ENVIRONMENT") or "YOUR_ENV"
openai_api_key = os.getenv("OPENAI_API_KEY")

DEMO_VECTOR_TYPE = "demo-search"
VECTOR_TYPE = "search"
IS_DEMO = True

def process(payload):
    guild_id = payload.get("guild_id")
    thread_id = payload.get("thread_id")
    title = payload.get("title")
    messages = payload.get("messages")
    created_at = payload.get("created_at")
    owner_id = payload.get("owner_id")

     # Process DATA and upload
    date_object = parser.parse(created_at)
    created_at = date_object.timestamp()

    thread_link = f"https://discord.com/channels/{guild_id}/{thread_id}"

    client = OpenAI(api_key=openai_api_key)
    pc = Pinecone(api_key=pinecone_api_key)

    index_name = "zkappumstad"
    model_name = "text-embedding-3-small"

    index = pc.Index(index_name)

    if IS_DEMO:
        vector_type = DEMO_VECTOR_TYPE
    else:
        vector_type = VECTOR_TYPE

    vector_id = str(uuid4())
    embedding_response = client.embeddings.create(
        input=title + " " + messages, model=model_name
    )

    embedding = embedding_response.data[0].embedding

    metadata = {
        "vector_type": vector_type,
        "guild_id": guild_id,
        "thread_id": thread_id,
        "title": title,
        "messages": messages,
        "created_at": created_at,
        "owner_id": owner_id,
        "thread_link": thread_link,
    }

    vector = {"id": vector_id, "values": embedding, "metadata": metadata}

    response = index.upsert(vectors=[vector])

    print(response)
    return {"statusCode": 200, "body": json.dumps(metadata)}

with open('payloads.json', 'r') as file:
    data = json.load(file)

for item in data:
    response = process(item)
    if response.get("statusCode") == 200:
        print(item, "Succesfully upserted")
    else:
        continue


