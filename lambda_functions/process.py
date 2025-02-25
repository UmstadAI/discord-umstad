# Example Thread Link: https://discord.com/channels/1153348653122076673/1213075628748709898
# Guild ID + Thread ID
# Example Message Link: https://discord.com/channels/1153348653122076673/1213072868175384587/1213084598603354172
# Guild ID + Thread ID + Message ID

import json
import os
import logging
from typing import Dict, Any, Optional, Union
from openai import OpenAI
from pinecone import Pinecone
from dateutil import parser
from uuid import uuid4
from dotenv import load_dotenv, find_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
_ = load_dotenv(find_dotenv(), override=True)  # read local .env file

# Environment configuration with better error handling
def get_env_var(var_name: str, default: Optional[str] = None, required: bool = True) -> str:
    """Get environment variable with validation"""
    value = os.getenv(var_name, default)
    if required and (value is None or value == "YOUR_API_KEY" or value == "YOUR_ENV"):
        raise EnvironmentError(f"Required environment variable {var_name} is not properly set")
    return value

# API keys and configuration
PINECONE_API_KEY = get_env_var("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = get_env_var("PINECONE_ENVIRONMENT", required=False)
OPENAI_API_KEY = get_env_var("OPENAI_API_KEY")
INDEX_NAME = get_env_var("PINECONE_INDEX_NAME", "zkappumstad")
MODEL_NAME = get_env_var("EMBEDDING_MODEL", "text-embedding-3-small")
IS_DEMO = os.getenv("IS_DEMO", "True").lower() in ("true", "1", "t")


def lambda_handler(event: Union[Dict[str, Any], Any], context: Optional[Any] = None) -> Dict[str, Any]:
    """
    Process a Discord message and store in vector database
    
    Args:
        event: Event data containing message information
        context: Lambda context (optional)
        
    Returns:
        Dict with status code and metadata
    """
    try:
        # Constants
        DEMO_VECTOR_TYPE = "demo-search"
        VECTOR_TYPE = "search"
        
        # Extract data from event
        guild_id = event.get("guild_id")
        thread_id = event.get("thread_id")
        title = event.get("title")
        message = event.get("message")
        message_id = event.get("message_id")
        created_at = event.get("created_at")
        owner_id = event.get("owner_id")
        
        # Validate required fields
        if not all([guild_id, thread_id, title, message, created_at, owner_id]):
            missing = [k for k in ["guild_id", "thread_id", "title", "message", "created_at", "owner_id"] 
                      if not event.get(k)]
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        # Process timestamp
        date_object = parser.parse(created_at)
        created_at_timestamp = date_object.timestamp()

        # Generate links
        thread_link = f"https://discord.com/channels/{guild_id}/{thread_id}"
        message_link = f"{thread_link}/{message_id}" if message_id else thread_link
        
        # Log message data
        logger.info(f"Processing message in thread: {thread_id}")
        logger.info(f"Title: {title}")
        logger.debug(f"Message content length: {len(message)}")
        logger.debug(f"Message ID: {message_id}")
        
        # Initialize clients
        client = OpenAI(api_key=OPENAI_API_KEY)
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(INDEX_NAME)

        # Determine vector type based on environment
        vector_type = DEMO_VECTOR_TYPE if IS_DEMO else VECTOR_TYPE

        # Generate embedding
        vector_id = str(uuid4())
        embedding_response = client.embeddings.create(
            input=title + " " + message, 
            model=MODEL_NAME
        )
        embedding = embedding_response.data[0].embedding

        # Prepare metadata
        metadata = {
            "vector_type": vector_type,
            "guild_id": guild_id,
            "thread_id": thread_id,
            "title": title,
            "message": message,
            "message_id": message_id,
            "created_at": created_at_timestamp,
            "owner_id": owner_id,
            "thread_link": thread_link,
            "message_link": message_link,
        }

        # Create and upsert vector
        vector = {"id": vector_id, "values": embedding, "metadata": metadata}
        response = index.upsert(vectors=[vector])

        logger.info(f"Successfully processed message {message_id} in thread {thread_id}")
        return {"statusCode": 200, "body": json.dumps(metadata)}
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
