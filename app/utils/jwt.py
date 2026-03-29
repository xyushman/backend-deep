from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "KRISHIDEEP_SECRET"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_minutes=60):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
from fastapi import FastAPI, HTTPException
from app.models.user import UserLogin
from app.utils.security import verify_password
from app.utils.jwt import create_access_token

app = FastAPI()

# Dummy user (for demo)
FAKE_USER_DB = {
    "mahima@gmail.com": {
        "email": "mahima@gmail.com",
        "password": "$2b$12$examplehashedpassword"
    }
}

@app.post("/login")
def login(user: UserLogin):
    db_user = FAKE_USER_DB.get(user.email)

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }
