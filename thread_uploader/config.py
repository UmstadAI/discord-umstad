from typing import Dict, List, Optional
from pydantic import BaseSettings, Field, HttpUrl
import os
from dotenv import load_dotenv

load_dotenv(override=True)

class ThreadUploaderConfig(BaseSettings):
    # Discord Configuration
    DISCORD_TOKEN: str = Field(env='THERAD_UPLOADER_DISCORD_TOKEN')
    GUILD_ID: int = Field(env='GUILD_ID')
    FORUM_ID: int = Field(env='FORUM_ID')
    
    # Thread Processing
    SOLVED_TAG: str = "solved"
    SOLVED_REACTION: str = "✅"
    AUTHORIZED_SOLVED_USERS: List[int] = Field(default_factory=list)
    MAX_THREADS_PER_SCAN: int = Field(default=100)
    SCAN_INTERVAL_HOURS: int = Field(default=24)
    
    # Lambda Configuration
    LAMBDA_THREAD_PROCESSOR_ENDPOINT: HttpUrl
    IS_THREAD_PROCESSOR_DONE: bool = Field(default=True)
    LAMBDA_TIMEOUT_SECONDS: int = Field(default=10)
    MAX_RETRIES: int = Field(default=3)
    RETRY_DELAY_SECONDS: int = Field(default=1)
    
    # Database Configuration
    DB_PATH: str = Field(default="db.json")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Metrics Configuration
    ENABLE_METRICS: bool = Field(default=True)
    METRICS_PORT: int = Field(default=9090)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global config instance
config = ThreadUploaderConfig() 