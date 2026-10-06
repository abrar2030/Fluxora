from app.core.error_middleware import add_error_handlers
from fastapi import FastAPI
from fastapi.testclient import TestClient


def _app() -> FastAPI:
    app = FastAPI()
    add_error_handlers(app)

    @app.get("/boom")
    def boom():
        raise RuntimeError("secret internal detail")

    return app


def test_unhandled_exception_does_not_leak_internals():
    client = TestClient(_app(), raise_server_exceptions=False)
    response = client.get("/boom")
    assert response.status_code == 500
    body = response.text
    assert "secret internal detail" not in body
    assert "Traceback" not in body
    assert response.json()["error"]["code"] == "INTERNAL_SERVER_ERROR"
