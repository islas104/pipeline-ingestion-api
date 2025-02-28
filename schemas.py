from pydantic import BaseModel
from typing import Dict

class SubmissionCreate(BaseModel):
    odk_id: str
    data: Dict
    geolocation: str  # WKT format (e.g., "POINT(-0.127758 51.507351)")

class SubmissionResponse(SubmissionCreate):
    id: int

    class Config:
        from_attributes = True  # Ensures ORM compatibility
