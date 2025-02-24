import requests
import sys
import os
import logging
import asyncio
from typing import Optional, List
from requests.exceptions import RequestException

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from process_thread import process_thread
from config import config
from metrics import track_time, increment_lambda_requests, increment_threads_processed

logger = logging.getLogger(__name__)

async def call_lambda_with_retry(payload: dict) -> bool:
    """
    Call Lambda API with retry logic.
    
    Args:
        payload: The payload to send to Lambda
        
    Returns:
        bool: True if the call was successful, False otherwise
    """
    for attempt in range(config.MAX_RETRIES):
        try:
            lambda_response = requests.post(
                str(config.LAMBDA_THREAD_PROCESSOR_ENDPOINT),
                json=payload,
                timeout=config.LAMBDA_TIMEOUT_SECONDS
            )
            lambda_response.raise_for_status()
            increment_lambda_requests("success")
            return True
            
        except RequestException as e:
            increment_lambda_requests("retry" if attempt < config.MAX_RETRIES - 1 else "failure")
            if attempt < config.MAX_RETRIES - 1:
                wait_time = config.RETRY_DELAY_SECONDS * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {str(e)}")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"All retry attempts failed: {str(e)}")
                return False
    
    return False

@track_time("handle_tagged")
async def handle_tagged(thread) -> Optional[bool]:
    """
    Handle a tagged thread and process it if marked as solved.
    
    Args:
        thread: Discord thread object
        
    Returns:
        bool: True if thread was successfully processed, False otherwise
        None: If thread was not eligible for processing
    """
    try:
        if thread.parent_id != config.FORUM_ID:
            logger.debug(f"Thread {thread.id} is not from target forum")
            return None
            
        includes_tag = any(tag.name == config.SOLVED_TAG for tag in thread.applied_tags)
        if not includes_tag:
            logger.debug(f"Thread {thread.id} does not have solved tag")
            return None
            
        logger.info(f"Processing solved thread {thread.id}")
        payload = await process_thread(thread)

        if not config.IS_THREAD_PROCESSOR_DONE:
            logger.info("Thread processor is not ready")
            return False

        success = await call_lambda_with_retry(payload)
        increment_threads_processed(success)
        return success
            
    except Exception as e:
        logger.error(f"Unexpected error processing thread {thread.id}: {str(e)}")
        increment_threads_processed(False)
        return False

@track_time("handle_reacted")
async def handle_reacted(thread) -> Optional[bool]:
    """
    Handle a thread that has been reacted to with the solved reaction.
    
    Args:
        thread: Discord thread object
        
    Returns:
        bool: True if thread was successfully processed, False otherwise
        None: If thread was not eligible for processing
    """
    try:
        if thread.parent_id != config.FORUM_ID:
            logger.debug(f"Thread {thread.id} is not from target forum")
            return None
            
        message = await thread.fetch_message(thread.id)
        reacted_solved_users: List[int] = []
        
        for reaction in message.reactions:
            if str(reaction.emoji) == config.SOLVED_REACTION:
                async for user in reaction.users():
                    reacted_solved_users.append(user.id)

        authorized_solved = any(
            user_id in config.AUTHORIZED_SOLVED_USERS 
            for user_id in reacted_solved_users
        )

        if not authorized_solved:
            logger.debug(f"Thread {thread.id} not marked as solved by authorized user")
            return None
            
        logger.info(f"Processing solved thread {thread.id} (reaction)")
        payload = await process_thread(thread)

        if not config.IS_THREAD_PROCESSOR_DONE:
            logger.info("Thread processor is not ready")
            return False

        success = await call_lambda_with_retry(payload)
        increment_threads_processed(success)
        return success
            
    except Exception as e:
        logger.error(f"Unexpected error processing thread {thread.id}: {str(e)}")
        increment_threads_processed(False)
        return False
