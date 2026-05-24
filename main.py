from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
import joblib
import json
from sqlalchemy.orm import Session
from database import SessionLocal, User, Prediction
from auth import get_user_by_api_key, hash_password, generate_api_key

# ----- NEW IMPORTS FOR RATE LIMITING -----
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

app = FastAPI(title="Secure Prediction API")

# ----- NEW RATE LIMITING SETUP -----
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

# Load the trained model
model = joblib.load("model.pkl")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Input schema
class PredictionInput(BaseModel):
    study_hours: float
    attendance: float
    prev_grade: float

# 1. SIGNUP ENDPOINT (Public - No API key needed)
@app.post("/signup")
def signup(username: str, password: str, db: Session = Depends(get_db)):
    # ... (your existing signup code)
    # ... (keep your signup code as is)

# 2. PREDICT ENDPOINT (Requires API key) - WITH RATE LIMITING
@app.post("/predict")
@limiter.limit("10/minute")  # 👈 THIS IS THE NEW LINE
def predict(input_data: PredictionInput, api_key: str = Header(..., alias="X-API-Key"), db: Session = Depends(get_db)):
    # Authenticate
    user = get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    # Input validation
    if input_data.study_hours < 0 or input_data.study_hours > 24:
        raise HTTPException(status_code=400, detail="study_hours must be between 0 and 24")
    if input_data.attendance < 0 or input_data.attendance > 100:
        raise HTTPException(status_code=400, detail="attendance must be between 0 and 100")
    if input_data.prev_grade < 0 or input_data.prev_grade > 100:
        raise HTTPException(status_code=400, detail="prev_grade must be between 0 and 100")
    
    # Run prediction
    features = [[input_data.study_hours, input_data.attendance, input_data.prev_grade]]
    prediction = model.predict(features)[0]
    
    # Save to database
    new_pred = Prediction(
        user_id=user.id,
        input_data=json.dumps(input_data.dict()),
        predicted_score=float(prediction)
    )
    db.add(new_pred)
    db.commit()
    
    return {"prediction": float(prediction)}

# 3. HISTORY ENDPOINT (Requires API key)
@app.get("/history")
def get_history(api_key: str = Header(..., alias="X-API-Key"), db: Session = Depends(get_db)):
    # ... (your existing history code)

# 4. ROOT ENDPOINT
@app.get("/")
def root():
    return {"message": "Secure Prediction API is running. Go to /docs for documentation."}
