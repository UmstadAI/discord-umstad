# DELETE SEARCH VECTORS, DEMO SEARCH VECTORS
import os
import numpy as np
from pinecone import Pinecone, ServerlessSpec

from uuid import uuid4
from dotenv import load_dotenv, find_dotenv

dimensions = 1536
random_vector = np.random.rand(dimensions).tolist()

RESET_TYPE = "demo-search-unanswered"

_ = load_dotenv(find_dotenv(), override=True)

pinecone_api_key = os.getenv("PINECONE_API_KEY") or "YOUR_API_KEY"
pinecone_env = os.getenv("PINECONE_ENVIRONMENT") or "YOUR_ENV"

pc = Pinecone(api_key=pinecone_api_key)
index_name = "zkappumstad"

index = pc.Index(index_name)

query_response = index.query(
    vector=random_vector,
    filter={
        "vector_type": RESET_TYPE
    },
    top_k=9999
)

matches = query_response['matches']
ids = [i['id'] for i in matches]
print(ids)
delete_response = index.delete(ids=ids)

print(f"Deleted {ids} vectors with vector_type {RESET_TYPE}")
