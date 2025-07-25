from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from packages.utilities.file_management.supabase_storage import upload_file, delete_file, generate_signed_url
from packages.database.config import SessionLocal
from packages.database.models import FileMetadata
from typing import List
from datetime import datetime
import os

router = APIRouter(prefix="/files", tags=["files"])

# Dependency to get DB session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Replace dummy auth with real get_current_user
try:
    from .profile_api import get_current_user
except ImportError:
    def get_current_user():
        class User:
            id = 1
        return User()

@router.post("/upload", status_code=201)
def upload_file_api(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Save to temp file
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(file.file.read())
    # Versioning: check for existing files with same filename
    existing = db.query(FileMetadata).filter_by(user_id=current_user.id, filename=file.filename).order_by(FileMetadata.version.desc()).first()
    version = 1
    if existing:
        version = existing.version + 1
    dest_path = f"user_{current_user.id}/v{version}_{datetime.utcnow().isoformat()}_{file.filename}"
    try:
        result = upload_file(temp_path, dest_path, content_type=file.content_type)
        # Save metadata
        meta = FileMetadata(
            user_id=current_user.id,
            filename=file.filename,
            storage_path=dest_path,
            file_type=file.content_type,
            size=os.path.getsize(temp_path),
            version=version,
            is_encrypted=result["is_encrypted"],
            is_compressed=result["is_compressed"],
            uploaded_at=datetime.utcnow(),
            file_metadata={"all_versions": [version] if not existing else (existing.file_metadata.get("all_versions", []) + [version])},
        )
        db.add(meta)
        db.commit()
        db.refresh(meta)
        return {"message": "File uploaded", "file_id": meta.id, "version": version}
    finally:
        os.remove(temp_path)

@router.get("/download/{file_id}")
def download_file_api(file_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    meta = db.query(FileMetadata).filter_by(id=file_id, user_id=current_user.id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="File not found")
    url = generate_signed_url(meta.storage_path)
    return {"url": url}

@router.get("/list", response_model=List[dict])
def list_files_api(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    files = db.query(FileMetadata).filter_by(user_id=current_user.id).all()
    return [
        {
            "id": f.id,
            "filename": f.filename,
            "uploaded_at": f.uploaded_at,
            "size": f.size,
            "file_type": f.file_type,
            "version": f.version,
        }
        for f in files
    ]

@router.delete("/delete/{file_id}")
def delete_file_api(file_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    meta = db.query(FileMetadata).filter_by(id=file_id, user_id=current_user.id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="File not found")
    delete_file(meta.storage_path)
    db.delete(meta)
    db.commit()
    return {"message": "File deleted"}
