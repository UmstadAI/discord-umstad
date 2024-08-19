import os
import numpy as np
from pinecone import Pinecone

from uuid import uuid4
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv(), override=True)

pinecone_api_key = os.getenv("PINECONE_API_KEY") or "YOUR_API_KEY"
pinecone_env = os.getenv("PINECONE_ENVIRONMENT") or "YOUR_ENV"
pc = Pinecone(api_key=pinecone_api_key)
index_name = "zkappumstad"
index = pc.Index(index_name)

dimensions = 1536
random_vector = np.random.rand(dimensions).tolist()
RESET_TYPE = "demo-search"

query_response = index.query(
    vector=random_vector, filter={"vector_type": RESET_TYPE}, top_k=99999
)

matches = query_response["matches"]
ids = [i["id"] for i in matches]

batch_size = 1000
for i in range(0, len(ids), batch_size):
    batch_ids = ids[i : i + batch_size]
    delete_response = index.delete(ids=batch_ids)
    print(f"Deleted {len(batch_ids)} vectors in this batch")

print(f"Deleted a total of {len(ids)} vectors with vector_type {RESET_TYPE}")
