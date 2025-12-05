import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuration
# Use an environment variable for the database URL, default to SQLite for simplicity
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fluxora.db")

# Create the SQLAlchemy engine
# connect_args is only needed for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models
Base = declarative_base()

def init_db():
    """Initializes the database by creating all tables."""
    # Import all models here so that they are registered with Base
    from Fluxora.code.models import user, data
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
