from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from starlette.responses import Response
from sqlalchemy.orm import Session
from xml.etree.ElementTree import Element, SubElement, tostring
from shapely.wkb import loads as wkb_loads
from src.database import engine, SessionLocal
from src.models import Submission
from src.schemas import SubmissionCreate
import json
import logging

# Initialize FastAPI app
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Pipeline Ingestion API"}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to convert dictionary/list to XML response
def dict_to_xml(data, root_tag="submission"):
    """
    Converts dictionary or list of dictionaries into a properly structured XML.
    """
    root = Element(root_tag)

    if isinstance(data, list):  # Handling multiple submissions
        for entry in data:
            submission_elem = SubElement(root, "submission")
            for key, value in entry.items():
                child = SubElement(submission_elem, key)
                if isinstance(value, dict):  
                    for sub_key, sub_value in value.items():
                        sub_child = SubElement(child, sub_key)
                        sub_child.text = str(sub_value)
                else:
                    child.text = str(value)
    else:  # Handling single submission
        for key, value in data.items():
            child = SubElement(root, key)
            if isinstance(value, dict):  
                for sub_key, sub_value in value.items():
                    sub_child = SubElement(child, sub_key)
                    sub_child.text = str(sub_value)
            else:
                child.text = str(value)

    return tostring(root)

@app.post("/submissions/")
def create_submission(
    submission: SubmissionCreate,
    db: Session = Depends(get_db),
    accept: str = Header(default="application/json")
):
    logger.info("Received submission request")

    try:
        # Insert data into DB
        db_submission = Submission(
            odk_id=submission.odk_id,
            data=json.dumps(submission.data),  # Ensure JSON object is stored correctly
            geolocation=f"SRID=4326;{submission.geolocation}"  # Ensure proper geolocation format
        )
        db.add(db_submission)
        db.commit()
        db.refresh(db_submission)

        # Convert WKB geolocation to WKT for proper serialization
        geolocation_wkt = None
        if db_submission.geolocation:
            geolocation_wkt = wkb_loads(bytes(db_submission.geolocation.data)).wkt

        # Ensure data is returned as a JSON object
        response_data = {
            "id": db_submission.id,
            "odk_id": db_submission.odk_id,
            "data": json.loads(db_submission.data),  # Convert back to JSON object
            "geolocation": geolocation_wkt,
        }

        logger.info(f"Data successfully stored: {response_data}")

        # Return XML if requested
        if "application/xml" in accept:
            return Response(content=dict_to_xml(response_data), media_type="application/xml")

        return JSONResponse(content=response_data)
    
    except Exception as e:
        logger.error(f"Error processing submission: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/submissions/")
def get_submissions(db: Session = Depends(get_db), accept: str = Header(default="application/json")):
    submissions = db.query(Submission).all()
    
    response_data = []
    for sub in submissions:
        try:
            data_parsed = json.loads(sub.data) if isinstance(sub.data, str) else sub.data
        except json.JSONDecodeError:
            data_parsed = sub.data  # Fallback if already a dict

        response_data.append({
            "id": sub.id,
            "odk_id": sub.odk_id,
            "data": data_parsed,
            "geolocation": wkb_loads(bytes(sub.geolocation.data)).wkt if sub.geolocation else None,
        })

    # Return XML if requested
    if "application/xml" in accept:
        return Response(content=dict_to_xml(response_data, root_tag="submissions"), media_type="application/xml")
    
    return JSONResponse(content=response_data)
