"""
Main API application stub for testing.
This is a minimal implementation to allow tests to run.
"""
from fastapi import FastAPI

app = FastAPI(title="Fluxora API", description="API for Fluxora", version="0.1.0")

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
