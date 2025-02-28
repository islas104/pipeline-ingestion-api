from sqlalchemy.orm import Session
from models import Submission
from schemas import SubmissionCreate

def create_submission(db: Session, submission: SubmissionCreate):
    db_submission = Submission(
        odk_id=submission.odk_id,
        data=submission.data,
        geolocation=submission.geolocation
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

def get_submission(db: Session, submission_id: int):
    return db.query(Submission).filter(Submission.id == submission_id).first()

def get_all_submissions(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Submission).offset(skip).limit(limit).all()
