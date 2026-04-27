"""
Request Timing Middleware

Measures how long each request takes to process.
Adds an X-Process-Time header to every response.

This is useful for:
- Performance monitoring
- Identifying slow endpoints
- Debugging latency issues
"""

import time
from fastapi import Request
from app.utils.loggers import logger


async def add_process_time_header(request: Request, call_next):
    """
    Function-based middleware that measures request processing time.
    
    This middleware:
    1. Records the start time before the endpoint runs
    2. Calls the next middleware/endpoint
    3. Records the end time after the response is ready
    4. Calculates the total duration
    5. Adds the duration to the response headers
    6. Logs the request with its duration
    
    Args:
        request: The incoming HTTP request
        call_next: Function to call the next layer
    
    Returns:
        Response: The HTTP response with timing header added
    """
    
    # ============================================
    # BEFORE THE ENDPOINT
    # ============================================
    # time.time() returns the current time in seconds (as a float)
    # Example: 1705330222.123456
    start_time = time.time()
    
    logger.debug(
        f"Request started: {request.method} {request.url.path}"
    )
    
    # ============================================
    # CALL THE ENDPOINT
    # ============================================
    # This is the critical line - it passes control to the next layer
    # The endpoint runs, and we wait for the response
    # With async/await, the server can handle other requests while waiting
    response = await call_next(request)
    
    # ============================================
    # AFTER THE ENDPOINT
    # ============================================
    # Calculate how long the request took
    # time.time() now gives a different (later) value
    end_time = time.time()
    
    # Calculate duration in seconds
    # Example: 1705330222.223456 - 1705330222.123456 = 0.100000
    duration_seconds = end_time - start_time
    
    # Convert to milliseconds for readability
    # 0.100000 seconds = 100.00 milliseconds
    duration_ms = round(duration_seconds * 1000, 2)
    
    # ============================================
    # ADD TIMING HEADER TO RESPONSE
    # ============================================
    # response.headers is a dictionary of HTTP headers
    # X- headers are custom (non-standard) headers
    # X-Process-Time tells clients exactly how long the server took
    response.headers["X-Process-Time"] = f"{duration_ms}ms"
    
    # ============================================
    # LOG THE REQUEST WITH TIMING
    # ============================================
    # Log at different levels based on duration
    # Slow requests get WARNING level for easy identification
    if duration_ms > 1000:
        # Request took more than 1 second - this is slow!
        logger.warning(
            f"SLOW REQUEST: {request.method} {request.url.path} "
            f"took {duration_ms}ms"
        )
    elif duration_ms > 500:
        # Request took more than 500ms - notable
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"took {duration_ms}ms"
        )
    else:
        # Normal fast request
        logger.debug(
            f"Request: {request.method} {request.url.path} "
            f"took {duration_ms}ms"
        )
    
    # ============================================
    # RETURN THE RESPONSE
    # ============================================
    # The response now has the X-Process-Time header
    return response