from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        api_key = request.headers.get("X-API-KEY")
        if not validate_api_key(api_key):
            return JSONResponse(
                status_code=403,
                content={"message": "Invalid API key"}
            )
        return await call_next(request)
