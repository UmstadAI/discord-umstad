# DELETE SEARCH VECTORS, DEMO SEARCH VECTORS
import os
from pinecone import Pinecone, ServerlessSpec

from uuid import uuid4
from dotenv import load_dotenv, find_dotenv

RESET_TYPE = "demo-search-unanswered"

_ = load_dotenv(find_dotenv(), override=True)

pinecone_api_key = os.getenv("PINECONE_API_KEY") or "YOUR_API_KEY"
pinecone_env = os.getenv("PINECONE_ENVIRONMENT") or "YOUR_ENV"

pc = Pinecone(api_key=pinecone_api_key)
index_name = "zkappumstad"

index = pc.Index(index_name)

response = index.delete(
    filter={
        "vector_type": RESET_TYPE
    }
)

print(f"Deleted {response} vectors with vector_type {RESET_TYPE}")
