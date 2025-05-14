"""
Model tests for Fluxora backend.
"""
import pytest
from datetime import datetime
from src.models.user import User
from src.models.base import Base

def test_user_model_creation(db_session):
    """Test user model creation and validation."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword123"
    )
    db_session.add(user)
    db_session.commit()
    
    # Test user was created
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.hashed_password == "hashedpassword123"
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)

def test_user_model_validation(db_session):
    """Test user model validation rules."""
    # Test email validation
    with pytest.raises(ValueError):
        User(
            email="invalid-email",
            username="testuser",
            hashed_password="hashedpassword123"
        )
    
    # Test username validation
    with pytest.raises(ValueError):
        User(
            email="test@example.com",
            username="",  # Empty username
            hashed_password="hashedpassword123"
        )
    
    # Test password validation
    with pytest.raises(ValueError):
        User(
            email="test@example.com",
            username="testuser",
            hashed_password=""  # Empty password
        )

def test_user_model_unique_constraints(db_session):
    """Test user model unique constraints."""
    # Create first user
    user1 = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword123"
    )
    db_session.add(user1)
    db_session.commit()
    
    # Try to create second user with same email
    user2 = User(
        email="test@example.com",  # Same email
        username="testuser2",
        hashed_password="hashedpassword456"
    )
    db_session.add(user2)
    with pytest.raises(Exception):  # Should raise unique constraint violation
        db_session.commit()
    
    db_session.rollback()
    
    # Try to create second user with same username
    user3 = User(
        email="test2@example.com",
        username="testuser",  # Same username
        hashed_password="hashedpassword789"
    )
    db_session.add(user3)
    with pytest.raises(Exception):  # Should raise unique constraint violation
        db_session.commit()

def test_user_model_relationships(db_session):
    """Test user model relationships."""
    # Create a user
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword123"
    )
    db_session.add(user)
    db_session.commit()
    
    # Test relationships are empty by default
    assert user.projects == []
    assert user.tasks == []
    assert user.comments == [] 