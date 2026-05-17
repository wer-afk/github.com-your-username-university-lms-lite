from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User, Assignment, Submission
from schemas import SubmissionCreate, SubmissionResponse, GradeSubmission


router = APIRouter(tags=["Submissions"])


@router.post("/submissions", response_model=SubmissionResponse)
def create_submission(submission: SubmissionCreate, db: Session = Depends(get_db)):
    student = db.query(User).filter(User.id == submission.student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if student.role != "student":
        raise HTTPException(status_code=400, detail="User is not a student")

    assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    new_submission = Submission(
        answer=submission.answer,
        student_id=submission.student_id,
        assignment_id=submission.assignment_id,
        grade=None
    )

    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)

    return new_submission


@router.get("/submissions", response_model=list[SubmissionResponse])
def get_submissions(db: Session = Depends(get_db)):
    return db.query(Submission).all()


@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
def get_submission(submission_id: int, db: Session = Depends(get_db)):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    return submission


@router.get("/assignments/{assignment_id}/submissions", response_model=list[SubmissionResponse])
def get_assignment_submissions(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    return db.query(Submission).filter(Submission.assignment_id == assignment_id).all()


@router.put("/submissions/{submission_id}/grade", response_model=SubmissionResponse)
def grade_submission(
    submission_id: int,
    grade_data: GradeSubmission,
    db: Session = Depends(get_db)
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if grade_data.grade < 0 or grade_data.grade > 100:
        raise HTTPException(status_code=400, detail="Grade must be between 0 and 100")

    submission.grade = grade_data.grade

    db.commit()
    db.refresh(submission)

    return submission


@router.delete("/submissions/{submission_id}")
def delete_submission(submission_id: int, db: Session = Depends(get_db)):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    db.delete(submission)
    db.commit()

    return {"message": "Submission deleted successfully"}