import os
import numpy as np
from pinecone import Pinecone, ServerlessSpec

from uuid import uuid4
from dotenv import load_dotenv, find_dotenv

dimensions = 1536
random_vector = np.random.rand(dimensions).tolist()

QUERY_TYPE = "demo-search"

_ = load_dotenv(find_dotenv(), override=True)

pinecone_api_key = os.getenv("PINECONE_API_KEY") or "YOUR_API_KEY"
pinecone_env = os.getenv("PINECONE_ENVIRONMENT") or "YOUR_ENV"

pc = Pinecone(api_key=pinecone_api_key)
index_name = "zkappumstad"

index = pc.Index(index_name)

query_response = index.query(
    vector=random_vector, filter={"vector_type": QUERY_TYPE}, top_k=9999, include_metadata=True
)

print(query_response)