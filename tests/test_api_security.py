from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from api_security import extract_bearer_token


app = FastAPI()


@app.get("/protected")
def protected(token: str = Depends(extract_bearer_token)):
    return {"token_seen": bool(token)}


def test_openapi_contains_bearer_scheme():
    schema = app.openapi()
    assert "BearerAuth" in schema["components"]["securitySchemes"]
    assert schema["components"]["securitySchemes"]["BearerAuth"]["scheme"] == "bearer"


def test_authorization_header_is_required():
    client = TestClient(app)
    response = client.get("/protected")
    assert response.status_code == 401


def test_bearer_token_is_extracted():
    client = TestClient(app)
    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer t23-test-token"},
    )
    assert response.status_code == 200
    assert response.json() == {"token_seen": True}
