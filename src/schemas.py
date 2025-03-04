from pydantic import BaseModel, Field

class SubmissionCreate(BaseModel):
    odk_id: str = Field(..., min_length=1)  # ✅ Ensure odk_id is non-empty
    data: dict
    geolocation: str  # Expected format: "POINT(longitude latitude)"

    class Config:
        from_attributes = True
