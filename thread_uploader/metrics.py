from prometheus_client import Counter, Histogram, start_http_server
import time
from functools import wraps
from typing import Callable
import logging

logger = logging.getLogger(__name__)

# Thread Processing Metrics
THREADS_PROCESSED = Counter(
    'thread_uploader_threads_processed_total',
    'Total number of threads processed',
    ['status']  # success, failure
)

THREAD_PROCESSING_TIME = Histogram(
    'thread_uploader_processing_duration_seconds',
    'Time spent processing threads',
    ['operation']  # scan, process_thread, lambda_call
)

LAMBDA_REQUESTS = Counter(
    'thread_uploader_lambda_requests_total',
    'Total number of Lambda API requests',
    ['status']  # success, failure, retry
)

def track_time(operation: str) -> Callable:
    """Decorator to track operation duration."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                THREAD_PROCESSING_TIME.labels(operation=operation).observe(duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                THREAD_PROCESSING_TIME.labels(operation=operation).observe(duration)
                raise e
        return wrapper
    return decorator

def init_metrics(port: int) -> None:
    """Initialize and start metrics server."""
    try:
        start_http_server(port)
        logger.info(f"Started metrics server on port {port}")
    except Exception as e:
        logger.error(f"Failed to start metrics server: {str(e)}")

def increment_threads_processed(success: bool) -> None:
    """Increment thread processing counter."""
    status = "success" if success else "failure"
    THREADS_PROCESSED.labels(status=status).inc()

def increment_lambda_requests(status: str) -> None:
    """Increment Lambda request counter."""
    LAMBDA_REQUESTS.labels(status=status).inc() 