# DELETE SEARCH VECTORS, DEMO SEARCH VECTORS
import os
from pinecone import Pinecone, ServerlessSpec

from uuid import uuid4
from dotenv import load_dotenv, find_dotenv

RESET_TYPE = "search"

_ = load_dotenv(find_dotenv(), override=True)

pinecone_api_key = os.getenv("PINECONE_API_KEY") or "YOUR_API_KEY"
pinecone_env = os.getenv("PINECONE_ENVIRONMENT") or "YOUR_ENV"

pc = Pinecone(api_key=pinecone_api_key)
index_name = "zkappumstad"

index = pinecone.Index(index_name)

query_result = index.query(
    "metadata.vector_type == {RESET_TYPE}", include_metadata=True, include_values=False
)

ids_to_delete = [
    item.id for item in query_result if item.metadata["vector_type"] == "search"
]

if ids_to_delete:
    index.delete(ids=ids_to_delete)

print(f"Deleted {len(ids_to_delete)} vectors with vector_type 'search'")
