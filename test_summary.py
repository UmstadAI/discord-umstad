import asyncio
import discord
import logging
import argparse
import datetime
from summary_bot import ChannelSummaryBot
from config import SUMMARY_CHANNEL_IDS, SUMMARY_LOOKBACK_HOURS

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def test_summary_generation(hours=None, channel_ids=None):
    """Test the summary generation functionality manually."""
    try:
        # Create an instance of the summary bot
        bot = ChannelSummaryBot()
        
        # Create a client connection using the bot's client
        await bot.client.login(bot.client.http.token)
        await bot.client.connect()
        
        # Wait for the bot to be ready
        while not bot.client.is_ready():
            await asyncio.sleep(1)
            
        logger.info("Bot is ready, generating summaries...")
        
        # Use provided parameters or defaults
        channels_to_summarize = channel_ids if channel_ids else SUMMARY_CHANNEL_IDS
        lookback_hours = hours if hours else SUMMARY_LOOKBACK_HOURS
        
        # Create cutoff time based on hours
        cutoff_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=lookback_hours)
        
        # Generate summaries
        summaries = await bot.generate_channel_summaries(channels_to_summarize, cutoff_time)
        
        # Print summaries to console for testing
        print(f"\n===== CHANNEL SUMMARIES (Last {lookback_hours} hours) =====\n")
        for summary in summaries:
            print(f"CHANNEL: #{summary['channel']}")
            print(f"SUMMARY: {summary['summary']}")
            print("="*60)
        
        logger.info("Test completed, closing connection...")
        await bot.client.close()
        
    except Exception as e:
        logger.error(f"Error testing summary generation: {e}")

if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Test Discord channel summarization')
    parser.add_argument('--hours', type=int, help='Number of hours to look back for messages')
    parser.add_argument('--channels', type=str, help='Comma-separated list of channel IDs to summarize')
    
    args = parser.parse_args()
    
    # Parse channel IDs if provided
    channel_ids = None
    if args.channels:
        channel_ids = [int(ch.strip()) for ch in args.channels.split(',') if ch.strip()]
    
    # Run the test
    asyncio.run(test_summary_generation(hours=args.hours, channel_ids=channel_ids)) 