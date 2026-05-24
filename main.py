from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
import joblib
import json
from sqlalchemy.orm import Session
from database import SessionLocal, User, Prediction
from auth import get_user_by_api_key

app = FastAPI(title="Secure Prediction API")

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

@app.post("/predict")
def predict(input_data: PredictionInput, api_key: str = Header(..., alias="X-API-Key"), db: Session = Depends(get_db)):
    user = get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    if input_data.study_hours < 0 or input_data.study_hours > 24:
        raise HTTPException(status_code=400, detail="study_hours must be between 0 and 24")
    if input_data.attendance < 0 or input_data.attendance > 100:
        raise HTTPException(status_code=400, detail="attendance must be between 0 and 100")
    if input_data.prev_grade < 0 or input_data.prev_grade > 100:
        raise HTTPException(status_code=400, detail="prev_grade must be between 0 and 100")
    
    features = [[input_data.study_hours, input_data.attendance, input_data.prev_grade]]
    prediction = model.predict(features)[0]
    
    new_pred = Prediction(
        user_id=user.id,
        input_data=json.dumps(input_data.dict()),
        predicted_score=float(prediction)
    )
    db.add(new_pred)
    db.commit()
    
    return {"prediction": float(prediction)}

@app.get("/history")
def get_history(api_key: str = Header(..., alias="X-API-Key"), db: Session = Depends(get_db)):
    user = get_user_by_api_key(db, api_key)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    predictions = db.query(Prediction).filter(Prediction.user_id == user.id).all()
    return [
        {
            "input_data": json.loads(p.input_data),
            "predicted_score": p.predicted_score,
            "timestamp": p.timestamp
        }
        for p in predictions
    ]

@app.get("/")
def root():
    return {"message": "Secure Prediction API is running. Go to /docs for documentation."}