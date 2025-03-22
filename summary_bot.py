import discord
import logging
import asyncio
import datetime
import schedule
import time
import os
from discord.ext import tasks
from openai import OpenAI
from collections import defaultdict
from config import (
    SUMMARY_BOT_DISCORD_TOKEN,
    SUMMARY_CHANNEL_IDS,
    SUMMARY_OUTPUT_CHANNEL_ID,
    SUMMARY_TIME,
    SUMMARY_LOOKBACK_HOURS,
    API_KEY,
    GUILD_ID
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class ChannelSummaryBot:
    def __init__(self):
        self.intents = discord.Intents.default()
        self.intents.messages = True
        self.intents.message_content = True
        self.intents.guilds = True

        self.client = discord.Client(intents=self.intents)
        self.openai_client = OpenAI(api_key=API_KEY)
        self.setup_events()
        
    def setup_events(self):
        @self.client.event
        async def on_ready():
            try:
                logger.info(f"Summary Bot logged in as {self.client.user}")
                # Start the daily summary task
                if not self.daily_summary.is_running():
                    # Parse the time for scheduling
                    hour, minute = map(int, SUMMARY_TIME.split(':'))
                    now = datetime.datetime.now()
                    
                    # Schedule the task to run at the specified time
                    self.daily_summary.start()
                    
                    logger.info(f"Daily summary scheduled for {SUMMARY_TIME}")
            except Exception as e:
                logger.error(f"Error during bot startup: {e}")
                
        @self.client.event
        async def on_message(message):
            try:
                # Ignore messages from the bot itself
                if message.author == self.client.user:
                    return
                
                # Check for manual summary command
                if message.content.startswith("!summarize"):
                    await self.handle_summarize_command(message)
            except Exception as e:
                logger.error(f"Error handling message: {e}")
    
    @tasks.loop(hours=24)
    async def daily_summary(self):
        """Generate and post daily summaries for the configured channels."""
        try:
            # Wait until the specified time
            now = datetime.datetime.now()
            target_time = now.replace(
                hour=int(SUMMARY_TIME.split(':')[0]),
                minute=int(SUMMARY_TIME.split(':')[1]),
                second=0,
                microsecond=0
            )
            
            # If the target time has already passed today, the task will run tomorrow
            if now > target_time:
                target_time = target_time + datetime.timedelta(days=1)
            
            # Calculate seconds until the target time
            seconds_until_target = (target_time - now).total_seconds()
            if seconds_until_target > 0:
                await asyncio.sleep(seconds_until_target)
            
            await self.generate_and_post_summaries()
            
        except Exception as e:
            logger.error(f"Error in daily summary task: {e}")
    
    async def handle_summarize_command(self, message):
        """Handle the manual summarize command."""
        try:
            # Parse the command - format: !summarize <hours> [channel_ids]
            parts = message.content.split()
            
            # Default to configured lookback hours if not specified
            hours = SUMMARY_LOOKBACK_HOURS
            # Default to configured channels
            channel_ids = SUMMARY_CHANNEL_IDS
            
            if len(parts) > 1:
                try:
                    # Try to parse hours parameter
                    hours = int(parts[1])
                except ValueError:
                    await message.channel.send("Invalid hours value. Please provide a number.")
                    return
            
            # If specific channels are provided
            if len(parts) > 2:
                try:
                    # Parse channel IDs - expected format: !summarize <hours> channel1,channel2,channel3
                    channel_input = " ".join(parts[2:])
                    if channel_input.strip():
                        # Try to parse as comma-separated list
                        if "," in channel_input:
                            channel_ids = [int(ch.strip()) for ch in channel_input.split(",") if ch.strip()]
                        # Try to parse as single channel ID
                        else:
                            channel_ids = [int(channel_input.strip())]
                except ValueError:
                    await message.channel.send("Invalid channel IDs. Please provide comma-separated numbers.")
                    return
            
            # Send acknowledgment
            await message.channel.send(f"Generating summaries for the last {hours} hours. This may take a few minutes...")
            
            # Create a custom cutoff time based on the requested hours
            cutoff_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=hours)
            
            # Generate summaries with the custom parameters
            summaries = await self.generate_channel_summaries(channel_ids, cutoff_time)
            
            # Post the summaries to the channel where the command was issued
            if summaries:
                today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                embed = discord.Embed(
                    title=f"Channel Summaries - {today}",
                    description=f"Summaries for the last {hours} hours",
                    color=discord.Color.blue()
                )
                
                for summary in summaries:
                    embed.add_field(
                        name=f"#{summary['channel']}",
                        value=summary['summary'][:1024],
                        inline=False
                    )
                
                await message.channel.send(embed=embed)
                logger.info(f"Posted summaries in response to manual command")
            else:
                await message.channel.send("No summaries were generated. The channels may be empty for the specified time period.")
                
        except Exception as e:
            logger.error(f"Error handling summarize command: {e}")
            await message.channel.send(f"Error generating summaries: {str(e)}")
    
    async def generate_and_post_summaries(self):
        """Collect messages from channels and generate summaries."""
        try:
            guild = self.client.get_guild(GUILD_ID)
            if not guild:
                logger.error(f"Could not find guild with ID {GUILD_ID}")
                return
            
            output_channel = guild.get_channel(SUMMARY_OUTPUT_CHANNEL_ID)
            if not output_channel:
                logger.error(f"Could not find output channel with ID {SUMMARY_OUTPUT_CHANNEL_ID}")
                return
            
            # Get the cutoff time for messages (X hours ago)
            cutoff_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=SUMMARY_LOOKBACK_HOURS)
            
            # Generate summaries
            channel_summaries = await self.generate_channel_summaries(SUMMARY_CHANNEL_IDS, cutoff_time)
            
            # Create and send the full summary
            if channel_summaries:
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                embed = discord.Embed(
                    title=f"Daily Channel Summaries - {today}",
                    color=discord.Color.blue()
                )
                
                for summary in channel_summaries:
                    embed.add_field(
                        name=f"#{summary['channel']}",
                        value=summary['summary'][:1024],  # Discord field value limit is 1024 characters
                        inline=False
                    )
                
                await output_channel.send(embed=embed)
                logger.info("Successfully posted daily channel summaries")
            else:
                logger.warning("No summaries were generated")
                
        except Exception as e:
            logger.error(f"Error generating and posting summaries: {e}")
    
    async def generate_channel_summaries(self, channel_ids, cutoff_time):
        """Generate summaries for the specified channels and time cutoff."""
        channel_summaries = []
        
        guild = self.client.get_guild(GUILD_ID)
        if not guild:
            logger.error(f"Could not find guild with ID {GUILD_ID}")
            return channel_summaries
        
        # Process each channel
        for channel_id in channel_ids:
            channel = guild.get_channel(channel_id)
            if not channel:
                logger.warning(f"Could not find channel with ID {channel_id}")
                continue
            
            channel_name = channel.name
            logger.info(f"Collecting messages from channel: {channel_name}")
            
            # Collect messages from the channel
            messages = []
            async for message in channel.history(after=cutoff_time, limit=None):
                # Skip bot messages if needed
                if message.author.bot:
                    continue
                
                messages.append({
                    "author": message.author.display_name,
                    "content": message.content,
                    "timestamp": message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                })
            
            if not messages:
                lookback_hours = int((datetime.datetime.now(datetime.timezone.utc) - cutoff_time).total_seconds() / 3600)
                logger.info(f"No messages found in channel {channel_name} in the last {lookback_hours} hours")
                channel_summaries.append({
                    "channel": channel_name,
                    "summary": f"No activity in the specified time period."
                })
                continue
            
            # Generate summary using OpenAI
            summary = await self.generate_summary(channel_name, messages)
            
            channel_summaries.append({
                "channel": channel_name,
                "summary": summary
            })
        
        return channel_summaries
    
    async def generate_summary(self, channel_name, messages):
        """Use OpenAI to generate a summary of the channel messages."""
        try:
            # Group messages by user
            user_messages = defaultdict(list)
            for msg in messages:
                user_messages[msg["author"]].append(f"{msg['timestamp']}: {msg['content']}")
            
            # Format messages for the prompt
            formatted_messages = []
            for user, msgs in user_messages.items():
                user_content = "\n".join(msgs)
                formatted_messages.append(f"User: {user}\nMessages:\n{user_content}\n")
            
            conversation_text = "\n".join(formatted_messages)
            
            # Check if the conversation is too long for a single API call
            if len(conversation_text) > 12000:  # Conservative limit to stay within token constraints
                return await self.generate_chunked_summary(channel_name, user_messages)
            
            # Prepare the prompt for OpenAI
            prompt = f"""
            Please summarize the following conversation from the Discord channel #{channel_name}.
            Focus on the main topics discussed, key decisions made, and any action items.
            Keep the summary concise but informative (150-200 words).
            
            Conversation:
            {conversation_text}
            """
            
            # Call OpenAI API for summarization
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # or gpt-3.5-turbo depending on your needs
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise summaries of Discord conversations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary for channel {channel_name}: {e}")
            return f"Error generating summary: {str(e)}"
    
    async def generate_chunked_summary(self, channel_name, user_messages):
        """Handle larger conversations by chunking them into smaller parts."""
        try:
            # Create chunks for each user's messages
            all_chunk_summaries = []
            
            # Process each user's messages separately
            for user, messages in user_messages.items():
                # If a single user has too many messages, chunk them
                if len("\n".join(messages)) > 6000:
                    # Split user messages into chunks (roughly by message count)
                    chunk_size = max(1, len(messages) // 4)  # Divide into ~4 chunks or less
                    message_chunks = [messages[i:i + chunk_size] for i in range(0, len(messages), chunk_size)]
                    
                    # Get summary for each chunk
                    user_chunk_summaries = []
                    for i, chunk in enumerate(message_chunks):
                        chunk_text = f"User: {user}\nMessages:\n" + "\n".join(chunk)
                        
                        prompt = f"""
                        Please summarize this portion ({i+1}/{len(message_chunks)}) of conversation from user {user} in Discord channel #{channel_name}.
                        Focus on the main topics and key points.
                        Keep it very brief (50 words max).
                        
                        Conversation excerpt:
                        {chunk_text}
                        """
                        
                        response = self.openai_client.chat.completions.create(
                            model="gpt-3.5-turbo",  # Using smaller model for intermediate summaries
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant that creates extremely concise summaries."},
                                {"role": "user", "content": prompt}
                            ],
                            max_tokens=100
                        )
                        
                        chunk_summary = response.choices[0].message.content.strip()
                        user_chunk_summaries.append(chunk_summary)
                    
                    # Add combined user summary
                    user_activity = f"User {user}: " + " ".join(user_chunk_summaries)
                else:
                    # For users with fewer messages, summarize all at once
                    chunk_text = f"User: {user}\nMessages:\n" + "\n".join(messages)
                    
                    prompt = f"""
                    Please summarize this user's activity in Discord channel #{channel_name}.
                    Focus on the main topics and key points.
                    Keep it very brief (50 words max).
                    
                    User activity:
                    {chunk_text}
                    """
                    
                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that creates extremely concise summaries."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=100
                    )
                    
                    user_activity = f"User {user}: " + response.choices[0].message.content.strip()
                
                all_chunk_summaries.append(user_activity)
            
            # Combine all intermediate summaries into a final summary
            combined_text = "\n".join(all_chunk_summaries)
            
            prompt = f"""
            Please create a final cohesive summary of the following Discord channel conversation excerpts.
            This is from channel #{channel_name}.
            Focus on the main topics discussed, key decisions made, and any action items.
            Keep the summary concise but informative (150-200 words).
            
            Individual summaries:
            {combined_text}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Using better model for final summary
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates well-organized, cohesive summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )
            
            final_summary = response.choices[0].message.content.strip()
            return final_summary
            
        except Exception as e:
            logger.error(f"Error generating chunked summary for channel {channel_name}: {e}")
            return f"Error generating summary due to large conversation volume: {str(e)}"
    
    def run(self):
        """Start the bot."""
        try:
            self.client.run(SUMMARY_BOT_DISCORD_TOKEN)
        except Exception as e:
            logger.critical(f"Failed to start summary bot: {e}")

if __name__ == "__main__":
    bot = ChannelSummaryBot()
    bot.run() 