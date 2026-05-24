import secrets
from sqlalchemy.orm import Session
from database import User
from argon2 import PasswordHasher

ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return ph.verify(hashed_password, plain_password)

def generate_api_key() -> str:
    return secrets.token_urlsafe(32)

def get_user_by_api_key(db: Session, api_key: str):
    return db.query(User).filter(User.api_key == api_key).first()