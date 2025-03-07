from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from starlette.responses import Response
from sqlalchemy.orm import Session
from xml.etree.ElementTree import Element, SubElement, tostring
from shapely.wkb import loads as wkb_loads
from src.database import SessionLocal
from src.models import Submission
from src.schemas import SubmissionCreate
import json
import logging
from shapely import wkt
from functools import lru_cache
from dotenv import load_dotenv
import os
import xml.etree.ElementTree as ET
from fastapi import Body

# Load environment variables once using lru_cache to prevent redundant calls
@lru_cache()
def get_env():
    load_dotenv()
    return {
        "DATABASE_URL": os.getenv("DATABASE_URL", "postgresql://ianawaz@localhost/pipeline_ingestion")
    }

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

# Convert dictionary/list to XML response
def dict_to_xml(data, root_tag="submission"):
    root = Element(root_tag)
    
    def build_xml(element, value):
        """Helper function to build XML recursively"""
        if isinstance(value, dict):
            for k, v in value.items():
                sub_elem = SubElement(element, k)
                build_xml(sub_elem, v)
        elif isinstance(value, list):
            for item in value:
                item_elem = SubElement(element, "item")
                build_xml(item_elem, item)
        else:
            element.text = str(value)

    if isinstance(data, list):  # Handling multiple submissions
        for entry in data:
            submission_elem = SubElement(root, "submission")
            for key, value in entry.items():
                child = SubElement(submission_elem, key)
                build_xml(child, value)
    else:  # Handling single submission
        for key, value in data.items():
            child = SubElement(root, key)
            build_xml(child, value)

    return tostring(root)

@app.post("/submissions/")
def create_submission(
    submission: SubmissionCreate,
    db: Session = Depends(get_db),
    accept: str = Header(default="application/json")
):
    logger.info("Received submission request")

    try:
        # ✅ Validate Geolocation Format Before Storing
        try:
            point = wkt.loads(submission.geolocation)  # Ensure it's a valid WKT
            geolocation_value = f"SRID=4326;{submission.geolocation}"
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid geolocation format")

        # ✅ Check for existing submission to update instead of inserting duplicate
        existing_submission = db.query(Submission).filter(Submission.odk_id == submission.odk_id).first()
        submission_data = json.dumps(submission.data) if isinstance(submission.data, dict) else submission.data

        if existing_submission:
            existing_submission.data = submission_data
            existing_submission.geolocation = geolocation_value
            db.commit()
            db.refresh(existing_submission)
            db_submission = existing_submission
        else:
            db_submission = Submission(
                odk_id=submission.odk_id,
                data=submission_data,
                geolocation=geolocation_value
            )
            db.add(db_submission)
            db.commit()
            db.refresh(db_submission)

        # Convert WKB geolocation to WKT safely
        geolocation_wkt = None
        if db_submission.geolocation:
            try:
                geolocation_wkt = wkb_loads(bytes(db_submission.geolocation.data)).wkt
            except Exception as e:
                logger.error(f"Error converting geolocation for submission {db_submission.id}: {str(e)}")

        response_data = {
            "id": db_submission.id,
            "odk_id": db_submission.odk_id,
            "data": json.loads(db_submission.data),
            "geolocation": geolocation_wkt,
        }

        logger.info(f"Data successfully stored: {response_data}")

        if "application/xml" in accept:
            return Response(content=dict_to_xml(response_data), media_type="application/xml")

        return JSONResponse(content=response_data)

    except HTTPException as e:
        raise e  # Let FastAPI handle expected validation errors
    except Exception as e:
        logger.error(f"Error processing submission: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/submissions/xml/")
def create_submission_xml(
    xml_body: str = Body(..., media_type="application/xml"),
    db: Session = Depends(get_db),
):
    try:
        # Parse the XML
        root = ET.fromstring(xml_body)
        odk_id = root.find("odk_id").text
        data = {child.tag: child.text for child in root.find("data")}
        geolocation = root.find("geolocation").text

        # Validate geolocation format
        try:
            wkt.loads(geolocation)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid geolocation format")

        # Store in DB
        submission = Submission(
            odk_id=odk_id,
            data=json.dumps(data),
            geolocation=f"SRID=4326;{geolocation}",
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        return {"id": submission.id, "odk_id": odk_id, "data": data, "geolocation": geolocation}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid XML format: {str(e)}")
    
@app.get("/submissions/")
def get_submissions(db: Session = Depends(get_db), accept: str = Header(default="application/json")):
    submissions = db.query(Submission).all()
    
    response_data = []
    for sub in submissions:
        try:
            data_parsed = json.loads(sub.data) if isinstance(sub.data, str) else sub.data
        except json.JSONDecodeError:
            data_parsed = sub.data  

        geolocation_wkt = None
        if sub.geolocation:
            try:
                geolocation_wkt = wkb_loads(bytes(sub.geolocation.data)).wkt
            except Exception as e:
                logger.error(f"Error converting geolocation for submission {sub.id}: {str(e)}")

        response_data.append({
            "id": sub.id,
            "odk_id": sub.odk_id,
            "data": data_parsed,
            "geolocation": geolocation_wkt,
        })

    if "application/xml" in accept:
        return Response(content=dict_to_xml(response_data, root_tag="submissions"), media_type="application/xml")

    return JSONResponse(content=response_data)
