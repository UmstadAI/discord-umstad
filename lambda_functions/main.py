from typing import Union, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, validator, Field
from process import lambda_handler
from thread_process import thread_lambda_handler
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Discord Thread Processor API",
    description="API for processing Discord threads and messages for vector search",
    version="1.0.0"
)

# uvicorn main:app --host 127.0.0.1 --port 8000


class Event(BaseModel):
    """
    Event model for processing Discord thread data.
    Either 'message' or 'messages' should be provided, but not both.
    """
    guild_id: str = Field(..., description="Discord guild/server ID")
    thread_id: str = Field(..., description="Discord thread ID")
    title: str = Field(..., description="Title of the thread")
    message: Union[str, None] = Field(None, description="Single message content")
    messages: Union[str, None] = Field(None, description="Multiple messages content")
    message_id: Union[str, None] = Field(None, description="Message ID for single message processing")
    created_at: str = Field(..., description="Creation timestamp")
    owner_id: str = Field(..., description="Owner's Discord ID")

    def get(self, key: str, default: Any = None) -> Any:
        """Get attribute value with a fallback default"""
        return getattr(self, key, default)

    @validator("message", "messages", pre=True, always=True)
    def check_not_both(cls, v, values, **kwargs):
        message_present = "message" in values and values["message"] is not None
        messages_present = "messages" in values and values["messages"] is not None

        if message_present and messages_present:
            raise ValueError(
                "Both 'message' and 'messages' cannot be provided simultaneously."
            )
        return v


@app.get("/", response_model=Dict[str, str])
async def read_root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Discord Thread Processor"}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all incoming requests"""
    logger.info(f"Request path: {request.url.path}")
    response = await call_next(request)
    return response


@app.post("/", response_model=Dict[str, Any])
async def consume_process(event: Event):
    """
    Process Discord thread or message data
    
    - If 'messages' is provided, processes multiple messages using thread_lambda_handler
    - If 'message' is provided, processes a single message using lambda_handler
    """
    try:
        logger.info(f"Processing event for thread: {event.thread_id}")
        
        if event.messages:
            response = thread_lambda_handler(event)
        else:
            response = lambda_handler(event)
            
        logger.info(f"Successfully processed thread: {event.thread_id}")
        return response
    except Exception as e:
        error_detail = f"Error processing event: {str(e)}"
        stack_trace = traceback.format_exc()
        logger.error(f"{error_detail}\n{stack_trace}")
        raise HTTPException(status_code=500, detail=error_detail)
