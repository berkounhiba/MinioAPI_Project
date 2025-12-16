from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import hashlib
import uuid
from io import BytesIO

from app.database import engine, get_db, Base
from app.models import FileMetadata
from app import minio_client


Base.metadata.create_all(bind=engine)

app = FastAPI(title="MinIO File Management API")

@app.get("/")
def root():
    return {"message": "MinIO API is running!"}

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    content = await file.read()
    sha256 = hashlib.sha256(content).hexdigest()
    object_name = f"{uuid.uuid4()}_{file.filename}"
    
    minio_client.upload_file(
        BytesIO(content),
        object_name,
        file.content_type
    )
    
    metadata = FileMetadata(
        filename=file.filename,
        minio_object_name=object_name,
        content_type=file.content_type,
        size=len(content),
        sha256_hash=sha256
    )
    db.add(metadata)
    db.commit()
    db.refresh(metadata)
    
    return {
        "id": metadata.id,
        "filename": file.filename,
        "size": len(content),
        "sha256": sha256,
        "message": "File uploaded successfully"
    }

@app.get("/files/{file_id}/metadata")
def get_metadata(file_id: int, db: Session = Depends(get_db)):
    metadata = db.query(FileMetadata).filter(FileMetadata.id == file_id).first()
    
    if not metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "id": metadata.id,
        "filename": metadata.filename,
        "content_type": metadata.content_type,
        "size": metadata.size,
        "sha256_hash": metadata.sha256_hash,
        "upload_date": metadata.upload_date
    }

@app.get("/download/{file_id}")
def download_file(file_id: int, db: Session = Depends(get_db)):
    metadata = db.query(FileMetadata).filter(FileMetadata.id == file_id).first()
    
    if not metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_data = minio_client.download_file(metadata.minio_object_name)
    
    return StreamingResponse(
        file_data,
        media_type=metadata.content_type,
        headers={"Content-Disposition": f"attachment; filename={metadata.filename}"}
    )

@app.delete("/delete/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db)):
    metadata = db.query(FileMetadata).filter(FileMetadata.id == file_id).first()
    
    if not metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    minio_client.delete_file(metadata.minio_object_name)
    db.delete(metadata)
    db.commit()
    
    return {"message": "File deleted successfully"}

@app.get("/files")
def list_files(db: Session = Depends(get_db)):
    files = db.query(FileMetadata).all()
    return {"files": files}

