"""
Dependencies module for API tests.
This is a stub implementation to allow tests to run.
"""
from typing import Generator
from sqlalchemy.orm import Session

def get_db() -> Generator[Session, None, None]:
    """
    Stub implementation of get_db dependency.
    Returns a mock session for testing.
    """
    # This is just a stub to allow tests to run
    yield None
