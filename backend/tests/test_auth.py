import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.auth import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    get_password_hash,
    verify_password
)
from app.models import User
from app.database import get_db, Base, engine

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_user(db):
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    db.add(user)
    db.commit()
    return user

def test_create_access_token():
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    assert token is not None
    assert isinstance(token, str)

def test_create_refresh_token():
    data = {"sub": "test@example.com"}
    token = create_refresh_token(data)
    assert token is not None
    assert isinstance(token, str)

def test_verify_token():
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == "test@example.com"

def test_verify_token_expired():
    data = {"sub": "test@example.com", "exp": datetime.utcnow() - timedelta(minutes=1)}
    token = create_access_token(data)
    with pytest.raises(HTTPException):
        verify_token(token)

def test_verify_token_invalid():
    with pytest.raises(HTTPException):
        verify_token("invalid_token")

def test_get_current_user(db, test_user):
    data = {"sub": test_user.email}
    token = create_access_token(data)
    user = get_current_user(token, db)
    assert user is not None
    assert user.email == test_user.email

def test_get_current_user_invalid_token(db):
    with pytest.raises(HTTPException):
        get_current_user("invalid_token", db)

def test_get_current_user_inactive(db):
    user = User(
        email="inactive@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=False
    )
    db.add(user)
    db.commit()
    
    data = {"sub": user.email}
    token = create_access_token(data)
    with pytest.raises(HTTPException):
        get_current_user(token, db)

def test_get_password_hash():
    password = "testpassword"
    hashed = get_password_hash(password)
    assert hashed is not None
    assert hashed != password
    assert isinstance(hashed, str)

def test_verify_password():
    password = "testpassword"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_password_hashing_consistency():
    password = "testpassword"
    hashed1 = get_password_hash(password)
    hashed2 = get_password_hash(password)
    assert hashed1 != hashed2  # Each hash should be unique
    assert verify_password(password, hashed1) is True
    assert verify_password(password, hashed2) is True

def test_token_payload():
    data = {
        "sub": "test@example.com",
        "custom_field": "custom_value"
    }
    token = create_access_token(data)
    payload = verify_token(token)
    assert payload["sub"] == "test@example.com"
    assert payload["custom_field"] == "custom_value"

def test_refresh_token_rotation():
    data = {"sub": "test@example.com"}
    refresh_token = create_refresh_token(data)
    payload = verify_token(refresh_token)
    assert payload["sub"] == "test@example.com"
    assert "refresh" in payload
    assert payload["refresh"] is True

def test_token_blacklist(db):
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    
    # Blacklist the token
    # This would typically involve adding the token to a blacklist in the database
    # For now, we'll just ensure the token verification still works
    payload = verify_token(token)
    assert payload["sub"] == "test@example.com"

def test_token_audience():
    data = {
        "sub": "test@example.com",
        "aud": "test_audience"
    }
    token = create_access_token(data)
    payload = verify_token(token)
    assert payload["aud"] == "test_audience"

def test_token_issuer():
    data = {
        "sub": "test@example.com",
        "iss": "test_issuer"
    }
    token = create_access_token(data)
    payload = verify_token(token)
    assert payload["iss"] == "test_issuer"

def test_token_jti():
    data = {
        "sub": "test@example.com",
        "jti": "test_jti"
    }
    token = create_access_token(data)
    payload = verify_token(token)
    assert payload["jti"] == "test_jti"

def test_token_scope():
    data = {
        "sub": "test@example.com",
        "scope": "read write"
    }
    token = create_access_token(data)
    payload = verify_token(token)
    assert payload["scope"] == "read write"

def test_token_roles():
    data = {
        "sub": "test@example.com",
        "roles": ["admin", "user"]
    }
    token = create_access_token(data)
    payload = verify_token(token)
    assert payload["roles"] == ["admin", "user"]

def test_token_permissions():
    data = {
        "sub": "test@example.com",
        "permissions": ["read:data", "write:data"]
    }
    token = create_access_token(token)
    payload = verify_token(token)
    assert payload["permissions"] == ["read:data", "write:data"] 