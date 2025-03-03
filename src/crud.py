from sqlalchemy.orm import Session
from src.models import Submission
from src.schemas import SubmissionCreate

def create_submission(db: Session, submission: SubmissionCreate):
    db_submission = Submission(
        odk_id=submission.odk_id,
        data=submission.data,
        geolocation=f"SRID=4326;{submission.geolocation}"  # Ensure SRID format
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

def get_submission(db: Session, submission_id: int):
    return db.query(Submission).filter(Submission.id == submission_id).first()

def get_all_submissions(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Submission).offset(skip).limit(limit).all()
