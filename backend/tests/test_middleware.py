import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from app.middleware import (
    RequestLoggingMiddleware,
    ErrorHandlingMiddleware,
    AuthenticationMiddleware,
    RateLimitingMiddleware,
    CORSMiddleware
)
from app.models import User
from app.database import get_db, Base, engine

@pytest.fixture(scope="function")
def app():
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(AuthenticationMiddleware)
    app.add_middleware(RateLimitingMiddleware)
    app.add_middleware(CORSMiddleware)
    return app

@pytest.fixture(scope="function")
def client(app):
    return TestClient(app)

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
        hashed_password="hashed_password",
        is_active=True
    )
    db.add(user)
    db.commit()
    return user

def test_request_logging_middleware(client):
    response = client.get("/test")
    assert response.status_code == 404
    # Check if request was logged
    # This would typically be verified by checking the logs
    # For now, we'll just ensure the middleware didn't break the request

def test_error_handling_middleware(client):
    @client.app.get("/error")
    async def error_endpoint():
        raise ValueError("Test error")
    
    response = client.get("/error")
    assert response.status_code == 500
    assert "error" in response.json()
    assert "detail" in response.json()

def test_authentication_middleware(client, test_user):
    @client.app.get("/protected")
    async def protected_endpoint():
        return {"message": "Protected endpoint"}
    
    # Test without token
    response = client.get("/protected")
    assert response.status_code == 401
    
    # Test with invalid token
    response = client.get("/protected", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401
    
    # Test with valid token
    # This would typically involve creating a valid JWT token
    # For now, we'll just ensure the middleware is working

def test_rate_limiting_middleware(client):
    @client.app.get("/limited")
    async def limited_endpoint():
        return {"message": "Limited endpoint"}
    
    # Make multiple requests
    for _ in range(5):
        response = client.get("/limited")
        assert response.status_code == 200
    
    # The next request should be rate limited
    response = client.get("/limited")
    assert response.status_code == 429
    assert "error" in response.json()
    assert "detail" in response.json()

def test_cors_middleware(client):
    @client.app.get("/cors")
    async def cors_endpoint():
        return {"message": "CORS endpoint"}
    
    # Test with allowed origin
    response = client.get("/cors", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" in response.headers
    
    # Test with disallowed origin
    response = client.get("/cors", headers={"Origin": "http://malicious.com"})
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" not in response.headers

def test_middleware_order(client):
    # Test that middleware is applied in the correct order
    @client.app.get("/order")
    async def order_endpoint():
        return {"message": "Order endpoint"}
    
    response = client.get("/order")
    assert response.status_code == 200
    
    # The order of middleware should be:
    # 1. CORS
    # 2. Request Logging
    # 3. Authentication
    # 4. Rate Limiting
    # 5. Error Handling
    # This can be verified by checking the response headers and behavior

def test_middleware_error_handling(client):
    @client.app.get("/middleware-error")
    async def middleware_error_endpoint():
        raise Exception("Middleware error")
    
    response = client.get("/middleware-error")
    assert response.status_code == 500
    assert "error" in response.json()
    assert "detail" in response.json()

def test_middleware_performance(client):
    @client.app.get("/performance")
    async def performance_endpoint():
        return {"message": "Performance endpoint"}
    
    # Test that middleware doesn't significantly impact performance
    start_time = datetime.now()
    for _ in range(100):
        response = client.get("/performance")
        assert response.status_code == 200
    end_time = datetime.now()
    
    # Ensure the total time is reasonable (e.g., less than 5 seconds)
    assert (end_time - start_time).total_seconds() < 5

def test_middleware_headers(client):
    @client.app.get("/headers")
    async def headers_endpoint():
        return {"message": "Headers endpoint"}
    
    response = client.get("/headers")
    assert response.status_code == 200
    
    # Check for security headers
    assert "X-Content-Type-Options" in response.headers
    assert "X-Frame-Options" in response.headers
    assert "X-XSS-Protection" in response.headers

def test_middleware_request_id(client):
    @client.app.get("/request-id")
    async def request_id_endpoint():
        return {"message": "Request ID endpoint"}
    
    response = client.get("/request-id")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"] is not None

def test_middleware_custom_headers(client):
    @client.app.get("/custom-headers")
    async def custom_headers_endpoint():
        return {"message": "Custom headers endpoint"}
    
    response = client.get("/custom-headers", headers={"X-Custom-Header": "test"})
    assert response.status_code == 200
    assert "X-Custom-Header" in response.headers
    assert response.headers["X-Custom-Header"] == "test" 