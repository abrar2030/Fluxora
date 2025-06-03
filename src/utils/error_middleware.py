import traceback
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from typing import Dict, Any, Optional

class ErrorDetail:
    """
    Error detail structure
    """
    def __init__(
        self,
        code: str,
        message: str,
        detail: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.detail = detail
        self.context = context or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation
        """
        result = {
            "code": self.code,
            "message": self.message
        }
        
        if self.detail:
            result["detail"] = self.detail
        
        if self.context:
            result["context"] = self.context
        
        return result

class ErrorResponse:
    """
    Standard error response structure
    """
    def __init__(
        self,
        error: ErrorDetail,
        request_id: Optional[str] = None,
        status_code: int = 500
    ):
        self.error = error
        self.request_id = request_id
        self.status_code = status_code
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation
        """
        result = {
            "error": self.error.to_dict()
        }
        
        if self.request_id:
            result["request_id"] = self.request_id
        
        return result

def add_error_handlers(app: FastAPI):
    """
    Add error handlers to the FastAPI application
    """
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Handle validation errors
        """
        error_detail = ErrorDetail(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            detail=str(exc),
            context={"errors": exc.errors()}
        )
        
        error_response = ErrorResponse(
            error=error_detail,
            request_id=request.headers.get("X-Request-ID"),
            status_code=400
        )
        
        return JSONResponse(
            status_code=400,
            content=error_response.to_dict()
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        Handle HTTP exceptions
        """
        error_detail = ErrorDetail(
            code=f"HTTP_{exc.status_code}",
            message=exc.detail,
            context=getattr(exc, "headers", None)
        )
        
        error_response = ErrorResponse(
            error=error_detail,
            request_id=request.headers.get("X-Request-ID"),
            status_code=exc.status_code
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.to_dict()
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """
        Handle generic exceptions
        """
        error_detail = ErrorDetail(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            detail=str(exc),
            context={"traceback": traceback.format_exc()}
        )
        
        error_response = ErrorResponse(
            error=error_detail,
            request_id=request.headers.get("X-Request-ID"),
            status_code=500
        )
        
        return JSONResponse(
            status_code=500,
            content=error_response.to_dict()
        )
