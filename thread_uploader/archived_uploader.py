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

vectors = []
index_name = "zkappumstad"
model_name = "text-embedding-3-small"
pc = Pinecone(api_key=pinecone_api_key)

index = pc.Index(index_name)

MAX_TOKENS = 4000  # Max tokens to stay under the limit

def chunk_messages(messages, max_tokens):
    chunks = []
    current_chunk = ""
    current_length = 0

    for message in messages.split():
        message_length = len(message)
        if current_length + message_length > max_tokens:
            chunks.append(current_chunk.strip())
            current_chunk = message + " "
            current_length = message_length
        else:
            current_chunk += message + " "
            current_length += message_length

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

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

    model_name = "text-embedding-3-small"

    if IS_DEMO:
        vector_type = DEMO_VECTOR_TYPE
    else:
        vector_type = VECTOR_TYPE

    vector_id = str(uuid4())
    
    message_chunks = chunk_messages(messages, MAX_TOKENS - len(title))
    
    for chunk in message_chunks:
        embedding_response = client.embeddings.create(
            input=title + " " + chunk, model=model_name
        )

        embedding = embedding_response.data[0].embedding

        metadata = {
            "vector_type": vector_type,
            "guild_id": guild_id,
            "thread_id": thread_id,
            "title": title,
            "messages": chunk,
            "created_at": created_at,
            "owner_id": owner_id,
            "thread_link": thread_link,
        }

        vector = (vector_id, embedding, metadata)
        vectors.append(vector)

    return True

with open("payloads.json", "r") as file:
    data = json.load(file)

for item in data:
    response = process(item)
    if response:
        print(item, "Successfully appended to Vectors array")
    else:
        continue

for i in range(0, len(vectors), 100):
    batch = vectors[i : i + 100]
    print("Upserting batch:", i)
    response = index.upsert(batch)
    print(response)