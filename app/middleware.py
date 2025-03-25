from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
import time
import logging
import traceback

logger = logging.getLogger("api_logger")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response: Response = await call_next(request)
        process_time = time.time() - start_time

        logger.info(
            f"{request.method} {request.url} - Status: {response.status_code} - Time: {process_time:.2f}s"
        )

        return response

class ExceptionLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(f"Unhandled Exception: {e}\n{error_trace}")
            return JSONResponse(
                status_code=500,
                content={"detail": "An unexpected error occurred."},
            )
