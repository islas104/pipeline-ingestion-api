from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import get_db, engine, Base
from models import Submission
from schemas import SubmissionCreate, SubmissionResponse
from sqlalchemy.sql import text

# Initialize FastAPI app
app = FastAPI()

# Ensure database tables are created
Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "ODK Pipeline Ingestion API is running"}

@app.post("/submissions/", response_model=SubmissionResponse)
async def create_submission(submission: SubmissionCreate, db: Session = Depends(get_db)):
    """
    Receives ODK submissions and stores them in the database.
    Supports structured data (JSON/XML) and geospatial data (WKT/GeoJSON).
    """
    try:
        db_submission = Submission(
            odk_id=submission.odk_id,
            data=submission.data,
            geolocation=f"SRID=4326;{submission.geolocation}"  # Ensure SRID format
        )
        db.add(db_submission)
        db.commit()
        db.refresh(db_submission)

        # Convert geolocation to WKT format before returning
        geolocation_wkt = db.execute(
            text("SELECT ST_AsText(geolocation) FROM submissions WHERE id = :id"),
            {"id": db_submission.id}
        ).fetchone()[0]

        return {
            "id": db_submission.id,
            "odk_id": db_submission.odk_id,
            "data": db_submission.data,
            "geolocation": geolocation_wkt  # Ensuring response is string format
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/submissions/{submission_id}", response_model=SubmissionResponse)
async def get_submission(submission_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a stored ODK submission by ID.
    """
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Convert geolocation to WKT format before returning
    geolocation_wkt = db.execute(
        text("SELECT ST_AsText(geolocation) FROM submissions WHERE id = :id"),
        {"id": submission.id}
    ).fetchone()[0]

    return {
        "id": submission.id,
        "odk_id": submission.odk_id,
        "data": submission.data,
        "geolocation": geolocation_wkt  # Ensuring response is string format
    }
