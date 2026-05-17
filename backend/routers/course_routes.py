from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from database import get_db
from models import User, Course
from schemas import CourseCreate, CourseResponse, CourseUpdate
from cache import redis_client, clear_courses_cache


router = APIRouter(tags=["Courses"])


@router.post("/courses", response_model=CourseResponse)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    teacher = db.query(User).filter(User.id == course.teacher_id).first()

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if teacher.role != "teacher":
        raise HTTPException(status_code=400, detail="User is not a teacher")

    new_course = Course(
        title=course.title,
        description=course.description,
        teacher_id=course.teacher_id
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    clear_courses_cache()

    return new_course


@router.get("/courses", response_model=list[CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    if redis_client:
        cached_courses = redis_client.get("courses_cache")

        if cached_courses:
            return json.loads(cached_courses)

    courses = db.query(Course).all()

    courses_data = [
        {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "teacher_id": course.teacher_id
        }
        for course in courses
    ]

    if redis_client:
        redis_client.setex(
            "courses_cache",
            60,
            json.dumps(courses_data)
        )

    return courses_data


@router.get("/courses/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    return course


@router.put("/courses/{course_id}", response_model=CourseResponse)
def update_course(course_id: int, course_data: CourseUpdate, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    teacher = db.query(User).filter(User.id == course_data.teacher_id).first()

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if teacher.role != "teacher":
        raise HTTPException(status_code=400, detail="User is not a teacher")

    course.title = course_data.title
    course.description = course_data.description
    course.teacher_id = course_data.teacher_id

    db.commit()
    db.refresh(course)

    clear_courses_cache()

    return course


@router.delete("/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    db.delete(course)
    db.commit()

    clear_courses_cache()

    return {"message": "Course deleted successfully"}