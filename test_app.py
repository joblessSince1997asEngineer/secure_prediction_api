from fastapi.testclient import TestClient
from main import app
from database import SessionLocal, User
from auth import generate_api_key, hash_password
import pytest
import secrets

client = TestClient(app)

# Override the database for testing
@pytest.fixture
def test_db():
    from database import engine, Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Secure Prediction API is running. Go to /docs for documentation."

def test_signup():
    username = f"testuser1_{secrets.token_hex(4)}"
    response = client.post(f"/signup?username={username}&password=testpass123")
    assert response.status_code == 200
    data = response.json()
    assert "api_key" in data
    assert data["username"] == username

def test_signup_duplicate():
    username = f"duplicate_{secrets.token_hex(4)}"
    client.post(f"/signup?username={username}&password=pass")
    response = client.post(f"/signup?username={username}&password=pass")
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"

def test_predict_no_key():
    response = client.post("/predict", json={"study_hours": 10, "attendance": 85, "prev_grade": 70})
    assert response.status_code == 422
    assert "X-API-Key" in response.text

def test_predict_invalid_key():
    username = f"testpredict_{secrets.token_hex(4)}"
    signup_resp = client.post(f"/signup?username={username}&password=pass")
    assert signup_resp.status_code == 200
    api_key = signup_resp.json()["api_key"]
    
    invalid_key = api_key[:-1] + "x"
    response = client.post(
        "/predict",
        headers={"X-API-Key": invalid_key},
        json={"study_hours": 10, "attendance": 85, "prev_grade": 70}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API Key"

def test_predict_invalid_input():
    username = f"validuser_{secrets.token_hex(4)}"
    signup_resp = client.post(f"/signup?username={username}&password=pass")
    assert signup_resp.status_code == 200
    api_key = signup_resp.json()["api_key"]

    response = client.post(
        "/predict",
        headers={"X-API-Key": api_key},
        json={"study_hours": 100, "attendance": 85, "prev_grade": 70}
    )
    assert response.status_code == 400
    assert "study_hours must be between 0 and 24" in response.json()["detail"]

def test_predict_valid():
    username = f"validuser2_{secrets.token_hex(4)}"
    signup_resp = client.post(f"/signup?username={username}&password=pass")
    assert signup_resp.status_code == 200
    api_key = signup_resp.json()["api_key"]

    response = client.post(
        "/predict",
        headers={"X-API-Key": api_key},
        json={"study_hours": 10, "attendance": 85, "prev_grade": 70}
    )
    assert response.status_code == 200
    assert "prediction" in response.json()