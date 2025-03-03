from sqlalchemy import Column, Integer, String, JSON
from geoalchemy2 import Geometry
from src.database import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    odk_id = Column(String, index=True)
    data = Column(JSON, nullable=False)
    geolocation = Column(Geometry("POINT", srid=4326), nullable=True)
