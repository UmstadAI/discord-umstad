import discord
import logging
from config import DISCORD_TOKEN, GUILD_ID
from commands import handle_command, handle_slash_command
from message import handle_message
from forum_listener import handle_thread_create
from dotenv import load_dotenv
from discord import app_commands

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv(override=True)


class UmstadBot:
    def __init__(self):
        self.intents = discord.Intents.default()
        self.intents.messages = True
        self.intents.message_content = True
        self.intents.guilds = True

        self.client = discord.Client(intents=self.intents)
        self.tree = app_commands.CommandTree(self.client)
        self.setup_events()

    def setup_events(self):
        @self.client.event
        async def on_ready():
            try:
                await self.tree.sync(guild=discord.Object(id=GUILD_ID))
                logger.info(f"Bot logged in as {self.client.user}")
            except Exception as e:
                logger.error(f"Error during bot startup: {e}")

        @self.tree.command(
            name="umstad",
            description="Call umstad Command",
            guild=discord.Object(id=GUILD_ID),
        )
        async def on_command(
            interaction: discord.Interaction, msg: str, message_number: int
        ):
            try:
                await interaction.response.defer()
                channel = interaction.channel

                previous_messages = []
                if channel:
                    async for message in channel.history(limit=message_number):
                        chat_message = {message.author.name: message.content}
                        previous_messages.append(chat_message)
                else:
                    logger.warning("Command does not support this channel type")
                    return

                response = await handle_slash_command(msg, previous_messages)
                await interaction.followup.send(response)
            except Exception as e:
                logger.error(f"Error handling slash command: {e}")
                await interaction.followup.send(
                    "An error occurred while processing your command"
                )

        @self.client.event
        async def on_message(message):
            try:
                if message.author == self.client.user:
                    return
                if message.content.startswith("!"):
                    await handle_command(message)
                await handle_message(message)
            except Exception as e:
                logger.error(f"Error handling message: {e}")

        @self.client.event
        async def on_thread_create(thread):
            try:
                await handle_thread_create(thread)
            except Exception as e:
                logger.error(f"Error handling thread creation: {e}")

    def run(self):
        try:
            self.client.run(DISCORD_TOKEN)
        except Exception as e:
            logger.critical(f"Failed to start bot: {e}")


if __name__ == "__main__":
    bot = UmstadBot()
    bot.run()
