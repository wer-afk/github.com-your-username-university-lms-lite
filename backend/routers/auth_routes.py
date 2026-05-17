from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserCreate, UserLogin
from auth import hash_password, verify_password, create_token
from rate_limiter import login_rate_limiter


router = APIRouter(tags=["Authentication"])


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password=hash_password(user.password),
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id
    }


@router.post("/login")
def login(request: Request, user: UserLogin, db: Session = Depends(get_db)):
    client_ip = request.client.host

    if not login_rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Please try again later."
        )

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_token({
        "user_id": db_user.id,
        "role": db_user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }