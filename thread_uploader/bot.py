# Discord Bot has access a forum channel
# We will have already solved and archived threads, so this bot.py necessary only for recent threads

# Decide forum thread is answered or solved with tag: decide_if_solved.py
## We have tiny DB to store solved forum threads to prevent duplicates
## Get Active threads once a day, If active thread solved and not in the TinyDB:
### https://schedule.readthedocs.io/en/stable/
### SEND to Lambda API toProcess and Upsert it via Lambda Functions

## EXTRA: Process with gpt in other worker, and upsert into issue vector


# Gets the thread data
# Process the Data (not with gpt): Create actual processor also in lambda_functions
# Upsert it to Vector DB

import sys
import discord
import os
import time
import logging
from typing import List, Optional
from datetime import datetime, timedelta

from tinydb import TinyDB, Query
from tinydb.table import Document

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from config import config
from metrics import init_metrics, track_time
from decide_if_solved import handle_tagged, handle_reacted

from discord import app_commands
from discord.ext import commands, tasks

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Setup database
try:
    db = TinyDB(config.DB_PATH)
    logger.info(f"Successfully connected to database at {config.DB_PATH}")
except Exception as e:
    logger.error(f"Failed to connect to database: {str(e)}")
    sys.exit(1)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    """Handle bot startup and initialization."""
    try:
        await tree.sync(guild=discord.Object(id=config.GUILD_ID))
        logger.info(f"Successfully logged in as {client.user}")
        
        # Initialize metrics server if enabled
        if config.ENABLE_METRICS:
            init_metrics(config.METRICS_PORT)
            
        scan.start()
    except Exception as e:
        logger.error(f"Failed to initialize bot: {str(e)}")
        await client.close()

@track_time("get_active_threads")
async def get_active_threads(guild: discord.Guild, channel_id: int) -> List[discord.Thread]:
    """Get active threads from specified channel."""
    try:
        threads = await guild.active_threads()
        return [
            thread for thread in threads
            if thread.parent_id == channel_id
        ]
    except Exception as e:
        logger.error(f"Failed to fetch active threads: {str(e)}")
        return []

@track_time("process_thread")
async def process_thread(thread: discord.Thread) -> bool:
    """Process a single thread and store in database if successful."""
    try:
        # Try both methods of determining if thread is solved
        posted = await handle_tagged(thread)
        if posted is None:
            posted = await handle_reacted(thread)
            
        if posted:
            db.insert({
                "id": thread.id,
                "processed_at": datetime.now().isoformat(),
                "method": "tag" if await handle_tagged(thread) else "reaction"
            })
            logger.info(f"Successfully processed and stored thread {thread.id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to process thread {thread.id}: {str(e)}")
        return False

@tasks.loop(hours=config.SCAN_INTERVAL_HOURS)
@track_time("scan")
async def scan():
    """Scan for new threads and process them."""
    try:
        logger.info("Starting thread scan")
        guild = discord.utils.get(client.guilds, id=config.GUILD_ID)
        if not guild:
            logger.error(f"Could not find guild with ID {config.GUILD_ID}")
            return

        # Get active threads
        threads = await get_active_threads(guild, config.FORUM_ID)
        if not threads:
            logger.info("No active threads found")
            return

        # Filter out already processed threads
        query = Query()
        stored_thread_ids = {item["id"] for item in db.all()}
        new_threads = [
            thread for thread in threads
            if thread.id not in stored_thread_ids
        ][:config.MAX_THREADS_PER_SCAN]

        if not new_threads:
            logger.info("No new threads to process")
            return

        logger.info(f"Found {len(new_threads)} new threads to process")
        
        # Process new threads
        for thread in new_threads:
            await process_thread(thread)
            
        logger.info("Thread scan completed")
            
    except Exception as e:
        logger.error(f"Error during thread scan: {str(e)}")

@scan.before_loop
async def before_scan():
    await client.wait_until_ready()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

def main():
    try:
        client.run(config.DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
