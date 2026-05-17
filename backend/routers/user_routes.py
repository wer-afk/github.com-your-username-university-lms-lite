from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserResponse


router = APIRouter(tags=["Users"])


@router.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.get("/users/students", response_model=list[UserResponse])
def get_students(db: Session = Depends(get_db)):
    return db.query(User).filter(User.role == "student").all()


@router.get("/users/teachers", response_model=list[UserResponse])
def get_teachers(db: Session = Depends(get_db)):
    return db.query(User).filter(User.role == "teacher").all()