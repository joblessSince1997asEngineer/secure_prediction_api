from database import SessionLocal, Prediction

db = SessionLocal()
predictions = db.query(Prediction).all()

print(f"Total predictions: {len(predictions)}")
print("-" * 50)

for p in predictions:
    print(f"ID: {p.id}")
    print(f"Score: {p.predicted_score}")
    print(f"Data: {p.input_data}")
    print(f"Time: {p.timestamp}")
    print("-" * 50)

db.close()