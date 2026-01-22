from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
import time
import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    প্রতিটা request log করবে
    
    Logs:
    - Request method, path, client IP
    - Response status code
    - Processing time
    """
    
    async def dispatch(self, request: Request, call_next):
        # Request start time
        start_time = time.time()
        
        # Client info
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} from {client_ip}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add custom header
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log response
            logger.info(
                f"Response: {response.status_code} | Time: {process_time:.3f}s | Path: {request.url.path}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Request failed: {str(e)} | Path: {request.url.path}")
            raise

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Global rate limiting middleware
    
    Per-IP rate limiting (fallback যদি user authenticated না থাকে)
    """
    
    def __init__(self, app, max_requests: int = 100, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window  # seconds
        from app.core.cache import cache
        self.cache = cache
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Rate limit key
        current_window = int(time.time() / self.window)
        key = f"global_rate_limit:{client_ip}:{current_window}"
        
        # Check rate limit
        count = self.cache.increment(key, ttl=self.window)
        
        if count > self.max_requests:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Too many requests. Limit: {self.max_requests} per {self.window} seconds."
                }
            )
        
        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.max_requests - count))
        
        return response

def setup_cors(app):
    """
    CORS setup করবে
    
    Production এ specific origins allow করবে
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Production এ specific domains দিতে হবে
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )