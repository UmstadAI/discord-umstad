"""
Discord Thread Processing Lambda Functions

This package contains AWS Lambda functions for processing Discord threads and messages,
generating embeddings, and storing them in a vector database (Pinecone).

Main components:
- lambda_handler: Processes individual Discord messages
- thread_lambda_handler: Processes entire Discord threads with multiple messages
- FastAPI application for local testing and development
"""

__version__ = "1.0.0"
__author__ = "UMSTAD Team"

from .process import lambda_handler
from .thread_process import thread_lambda_handler

__all__ = ["lambda_handler", "thread_lambda_handler"]
