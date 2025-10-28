import asyncio
import uuid
import time
import json
from enum import Enum
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Text, Float, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import requests

# Database setup
DATABASE_URL = "sqlite:///./dlq.db"  # Use PostgreSQL in production
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DeadLetteredMessage(Base):
    __tablename__ = "dead_lettered_messages"
    
    id = Column(String, primary_key=True, index=True)
    source_queue = Column(String, index=True)
    destination_service = Column(String, index=True)
    payload = Column(Text)
    error_message = Column(Text)
    created_at = Column(Float)
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(Float, nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(Float, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

class MessageStatus(Enum):
    PENDING = "PENDING"
    RETRYING = "RETRYING"
    RESOLVED = "RESOLVED"
    FAILED = "FAILED"

class DeadLetteredMessageModel(BaseModel):
    source_queue: str
    destination_service: str
    payload: Dict[str, Any]
    error_message: str

app = FastAPI(title="Dead Letter Queue")

@app.post("/messages")
async def create_message(message: DeadLetteredMessageModel):
    """
    Create a new dead-lettered message
    """
    db = SessionLocal()
    try:
        message_id = str(uuid.uuid4())
        db_message = DeadLetteredMessage(
            id=message_id,
            source_queue=message.source_queue,
            destination_service=message.destination_service,
            payload=json.dumps(message.payload),
            error_message=message.error_message,
            created_at=time.time(),
            retry_count=0,
            last_retry_at=None,
            resolved=False,
            resolved_at=None
        )
        db.add(db_message)
        db.commit()
        return {"message_id": message_id, "status": MessageStatus.PENDING.value}
    finally:
        db.close()

@app.post("/messages/{message_id}/retry")
async def retry_message(message_id: str, background_tasks: BackgroundTasks):
    """
    Retry a dead-lettered message
    """
    db = SessionLocal()
    try:
        message = db.query(DeadLetteredMessage).filter(DeadLetteredMessage.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        if message.resolved:
            raise HTTPException(status_code=400, detail="Message already resolved")
        
        # Update retry count and timestamp
        message.retry_count += 1
        message.last_retry_at = time.time()
        db.commit()
        
        # Start retry in background
        background_tasks.add_task(retry_message_delivery, message_id)
        
        return {"message_id": message_id, "status": MessageStatus.RETRYING.value}
    finally:
        db.close()

@app.post("/messages/{message_id}/resolve")
async def resolve_message(message_id: str):
    """
    Mark a dead-lettered message as resolved
    """
    db = SessionLocal()
    try:
        message = db.query(DeadLetteredMessage).filter(DeadLetteredMessage.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        message.resolved = True
        message.resolved_at = time.time()
        db.commit()
        
        return {"message_id": message_id, "status": MessageStatus.RESOLVED.value}
    finally:
        db.close()

@app.get("/messages/{message_id}")
async def get_message(message_id: str):
    """
    Get message details
    """
    db = SessionLocal()
    try:
        message = db.query(DeadLetteredMessage).filter(DeadLetteredMessage.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        status = MessageStatus.RESOLVED.value if message.resolved else MessageStatus.PENDING.value
        
        return {
            "message_id": message.id,
            "source_queue": message.source_queue,
            "destination_service": message.destination_service,
            "payload": json.loads(message.payload),
            "error_message": message.error_message,
            "created_at": message.created_at,
            "retry_count": message.retry_count,
            "last_retry_at": message.last_retry_at,
            "resolved": message.resolved,
            "resolved_at": message.resolved_at,
            "status": status
        }
    finally:
        db.close()

@app.get("/messages")
async def list_messages(
    source_queue: Optional[str] = None,
    destination_service: Optional[str] = None,
    resolved: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    List dead-lettered messages with optional filtering
    """
    db = SessionLocal()
    try:
        query = db.query(DeadLetteredMessage)
        
        if source_queue:
            query = query.filter(DeadLetteredMessage.source_queue == source_queue)
        
        if destination_service:
            query = query.filter(DeadLetteredMessage.destination_service == destination_service)
        
        if resolved is not None:
            query = query.filter(DeadLetteredMessage.resolved == resolved)
        
        total = query.count()
        
        messages = query.order_by(DeadLetteredMessage.created_at.desc()).offset(offset).limit(limit).all()
        
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "messages": [
                {
                    "message_id": message.id,
                    "source_queue": message.source_queue,
                    "destination_service": message.destination_service,
                    "error_message": message.error_message,
                    "created_at": message.created_at,
                    "retry_count": message.retry_count,
                    "resolved": message.resolved,
                    "status": MessageStatus.RESOLVED.value if message.resolved else MessageStatus.PENDING.value
                }
                for message in messages
            ]
        }
    finally:
        db.close()

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

async def retry_message_delivery(message_id: str):
    """
    Retry delivery of a dead-lettered message
    """
    db = SessionLocal()
    try:
        message = db.query(DeadLetteredMessage).filter(DeadLetteredMessage.id == message_id).first()
        if not message or message.resolved:
            return
        
        try:
            # Get service URL from service registry
            service_url = get_service_url(message.destination_service)
            if not service_url:
                return
            
            # Send message to destination service
            response = requests.post(
                f"{service_url}/messages",
                json=json.loads(message.payload)
            )
            
            if response.status_code == 200:
                # Mark message as resolved
                message.resolved = True
                message.resolved_at = time.time()
                db.commit()
        except Exception as e:
            print(f"Error retrying message {message_id}: {str(e)}")
    finally:
        db.close()

def get_service_url(service_name: str) -> Optional[str]:
    """
    Get service URL from service registry
    """
    try:
        registry_url = "http://service-registry:8500"
        response = requests.get(f"{registry_url}/v1/catalog/service/{service_name}")
        if response.status_code == 200:
            services = response.json()
            if services:
                service = services[0]
                return f"http://{service['ServiceAddress']}:{service['ServicePort']}"
        return None
    except Exception as e:
        print(f"Error getting service URL: {str(e)}")
        return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
