from database import SessionLocal, User, Prediction
from auth import hash_password, generate_api_key

db = SessionLocal()

# Create a test user
test_user = User(
    username="testuser",
    hashed_password=hash_password("testpass123"),
    api_key=generate_api_key()
)
db.add(test_user)
db.commit()
print("Test user created ✅")
db.close()