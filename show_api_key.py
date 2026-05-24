from database import SessionLocal, User

db = SessionLocal()
user = db.query(User).first()
if user:
    print("Your API Key is:", user.api_key)
    print("")
    print("Test with curl:")
    print(f'curl -X POST "http://127.0.0.1:8000/predict" -H "X-API-Key: {user.api_key}" -H "Content-Type: application/json" -d \'{{"study_hours": 10, "attendance": 85, "prev_grade": 70}}\'')
db.close()