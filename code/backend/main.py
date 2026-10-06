import os

import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        workers=int(os.getenv("API_WORKERS", "1")),
        reload=os.getenv("ENV", "development") == "development",
    )

__all__ = ["app"]
