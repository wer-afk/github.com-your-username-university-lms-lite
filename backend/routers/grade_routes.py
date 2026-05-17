from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from database import get_db
from models import User, Course, Assignment, Submission


router = APIRouter(tags=["Grades"])


@router.get("/grades/export")
def export_grades(db: Session = Depends(get_db)):
    submissions = db.query(Submission).all()

    lines = []
    lines.append("ID,Student,Course,Assignment,Answer,Grade,Status")

    for submission in submissions:
        student = db.query(User).filter(User.id == submission.student_id).first()
        assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()

        course = None
        if assignment:
            course = db.query(Course).filter(Course.id == assignment.course_id).first()

        student_name = student.full_name if student else "Unknown student"
        course_title = course.title if course else "Unknown course"
        assignment_title = assignment.title if assignment else "Unknown assignment"
        answer = submission.answer if submission.answer else ""
        grade = str(submission.grade) if submission.grade is not None else "Not graded"
        status = "Graded" if submission.grade is not None else "Pending"

        student_name = student_name.replace(",", " ")
        course_title = course_title.replace(",", " ")
        assignment_title = assignment_title.replace(",", " ")
        answer = answer.replace("\n", " ").replace("\r", " ").replace(",", " ")

        line = f"{submission.id},{student_name},{course_title},{assignment_title},{answer},{grade},{status}"
        lines.append(line)

    csv_content = "\n".join(lines)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=grades_report.csv"
        }
    )