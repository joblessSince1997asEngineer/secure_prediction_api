# Secure Model Serving API

A secure backend API that serves ML predictions using FastAPI and scikit-learn.

## Features
- 🔐 API key authentication
- 📊 ML model (Linear Regression) to predict student performance
- 🗄️ Database storage (SQLite) for prediction history
- ✅ Input validation
- 📖 Auto-generated Swagger UI documentation

## Tech Stack
- Python 3
- FastAPI
- SQLAlchemy
- scikit-learn
- Argon2 (password hashing)

## How to Run
1. Clone the repo
2. Create venv: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows)
4. Install: `pip install -r requirements.txt`
5. Train model: `python train_model.py`
6. Run server: `uvicorn main:app --reload`
7. Open: `http://127.0.0.1:8000/docs`

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /predict | Predict score (requires API key) |
| GET | /history | View past predictions |
| GET | / | Root message |

## Test with curl