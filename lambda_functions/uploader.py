import glob
import os
import openai
import pinecone
import time
import re
import json

from uuid import uuid4
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv(), override=True)  # read local .env file

pinecone_api_key = os.getenv("PINECONE_API_KEY") or "YOUR_API_KEY"
pinecone_env = os.getenv("PINECONE_ENVIRONMENT") or "YOUR_ENV"

pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "OPENAI_API_KEY")

index_name = "zkappumstad"
model_name = "text-embedding-3-small"

VECTOR_TYPE = 'search'
