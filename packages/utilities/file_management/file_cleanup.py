import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from packages.database.config import SessionLocal
from packages.database.models import FileMetadata, User, InAppNotification, Skill, Project, Experience, Education, JobPreference
from packages.utilities.file_management.supabase_storage import delete_file
import secrets

# How many versions to keep per file
KEEP_VERSIONS = 3

def cleanup_old_file_versions():
    db: Session = SessionLocal()
    try:
        users = db.query(FileMetadata.user_id).distinct()
        for user_row in users:
            user_id = user_row.user_id
            # Get all files for user, grouped by filename
            files = db.query(FileMetadata).filter_by(user_id=user_id).all()
            by_name = {}
            for f in files:
                by_name.setdefault(f.filename, []).append(f)
            for fname, versions in by_name.items():
                # Sort by version descending (latest first)
                versions.sort(key=lambda x: x.version, reverse=True)
                # Keep only the latest N
                for old in versions[KEEP_VERSIONS:]:
                    print(f"Deleting old version: {old.filename} v{old.version} (id={old.id})")
                    delete_file(old.storage_path)
                    db.delete(old)
        db.commit()
    finally:
        db.close()

def secure_delete_file(file_path: str, passes: int = 3):
    """
    Overwrite a file with random data before deleting it (secure deletion).
    """
    if not os.path.exists(file_path):
        return
    length = os.path.getsize(file_path)
    with open(file_path, "ba+") as f:
        for _ in range(passes):
            f.seek(0)
            f.write(secrets.token_bytes(length))
            f.flush()
            os.fsync(f.fileno())
    os.remove(file_path)

def cleanup_old_user_data(retention_days: int = 730):
    """
    Delete user accounts and all related data that have not been active for more than retention_days.
    """
    db = SessionLocal()
    cutoff = datetime.utcnow() - timedelta(days=retention_days)
    old_users = db.query(User).filter(User.created_at < cutoff).all()
    for user in old_users:
        user_id = user.id
        db.query(InAppNotification).filter_by(user_id=user_id).delete()
        db.query(Skill).filter_by(user_id=user_id).delete()
        db.query(Project).filter_by(user_id=user_id).delete()
        db.query(Experience).filter_by(user_id=user_id).delete()
        db.query(Education).filter_by(user_id=user_id).delete()
        db.query(JobPreference).filter_by(user_id=user_id).delete()
        db.delete(user)
    db.commit()
    db.close()

if __name__ == "__main__":
    cleanup_old_file_versions()
    cleanup_old_user_data()
