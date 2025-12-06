from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .backend.database import init_db
from .api.v1 import auth, data, analytics, predictions

# Initialize the database (create tables)
init_db()

app = FastAPI(
    title="Fluxora API",
    description="API for energy data management and prediction.",
    version="1.0.0",
)

# CORS Middleware for frontend development
origins = [
    "http://localhost",
    "http://localhost:3000",  # React default port
    "http://localhost:5173",  # Vite default port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/v1")
app.include_router(data.router, prefix="/v1")
app.include_router(analytics.router, prefix="/v1")
app.include_router(predictions.router, prefix="/v1")


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}
