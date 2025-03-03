from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://ianawaz@localhost/pipeline_ingestion"

engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=10)  # Optimized for scalability
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
