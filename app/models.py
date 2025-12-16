from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class FileMetadata(Base):
    __tablename__ = "file_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    minio_object_name = Column(String, unique=True)
    content_type = Column(String)
    size = Column(Integer)
    sha256_hash = Column(String)
    upload_date = Column(DateTime, default=datetime.utcnow)