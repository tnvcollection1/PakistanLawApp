"""Rate limiting and anti-scraping middleware."""
import time
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter."""
    
    def __init__(self, app, max_requests=100, window=60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.requests = {}
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        
        # Clean old entries
        self.requests = {ip: times for ip, times in self.requests.items() 
                          if any(t > now - self.window for t in times)}
        
        # Check rate limit
        client_requests = self.requests.get(client_ip, [])
        recent_requests = [t for t in client_requests if t > now - self.window]
        
        if len(recent_requests) >= self.max_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Record request
        recent_requests.append(now)
        self.requests[client_ip] = recent_requests
        
        response = await call_next(request)
        return response
