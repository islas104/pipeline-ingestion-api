from pydantic import BaseModel

class SubmissionCreate(BaseModel):
    odk_id: str
    data: dict
    geolocation: str  # Expected format: "POINT(longitude latitude)"

    class Config:
        from_attributes = True  # ✅ Updated for Pydantic v2 compatibility
