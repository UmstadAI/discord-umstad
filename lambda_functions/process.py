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
import openai
import pinecone
import time
import re

from datetime import datetime
from dateutil import parser

from uuid import uuid4
from dotenv import load_dotenv, find_dotenv


def lambda_handler(event, context=None):
    DEMO_UNANSWERED_VECTOR_TYPE = "demo-search-unanswered"
    UNANSWERED_VECTOR_TYPE = "search-unanswered"
    IS_DEMO = True

    guild_id = event.get("guild_id")
    thread_id = event.get("thread_id")
    title = event.get("title")
    message = event.get("message")
    created_at = event.get("created_at")
    owner_id = event.get("owner_id")

    # Process DATA and upload
    date_object = parser.parse(created_at)
    created_at = date_object.timestamp()

    thread_link = "https://discord.com/channels/{GUILD_ID}/{thread_id}"
    message_link = thread_id + "/" + message_id #TODO: GET MESSAGE ID
    
    # LOG THE THREAD DATA
    print("Guild ID: ", guild_id)
    print("Thread ID:", thread_id)
    print("Title: ", title)
    print("Message: ", message)
    print("Created AT: ", created_at)
    print("Owner: ", owner_id)

    _ = load_dotenv(find_dotenv(), override=True)  # read local .env file

    pinecone_api_key = os.getenv("PINECONE_API_KEY") or "YOUR_API_KEY"
    pinecone_env = os.getenv("PINECONE_ENVIRONMENT") or "YOUR_ENV"

    pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "OPENAI_API_KEY")

    index_name = "zkappumstad"
    model_name = "text-embedding-3-small"

    if IS_DEMO:
        vector_type = DEMO_UNANSWERED_VECTOR_TYPE
    else:
        vector_type = UNANSWERED_VECTOR_TYPE

    metadata = {
        "guild_id": guild_id,
        "thread_id": thread_id,
        "title": title,
        "message": message,
        "created_at": created_at,
        "owner_id": owner_id,
    }

    return {"statusCode": 200, "body": json.dumps("AWS Lambda got the thread")}
