import os
from packages.database.config import SessionLocal
from packages.database.models import FileMetadata
from packages.utilities.encryption_utils import fernet

BACKUP_DIR = "output/file_backups"

os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_all_files(backup_dir: str = "./backups"):
    """
    Download and encrypt all files and their metadata to a local backup directory.
    """
    db = SessionLocal()
    os.makedirs(backup_dir, exist_ok=True)
    files = db.query(FileMetadata).all()
    for file in files:
        if not os.path.exists(file.storage_path):
            continue
        with open(file.storage_path, "rb") as f:
            file_bytes = f.read()
        encrypted_bytes = fernet.encrypt(file_bytes)
        backup_path = os.path.join(backup_dir, file.filename + ".enc")
        with open(backup_path, "wb") as f:
            f.write(encrypted_bytes)
        # Optionally, backup metadata as well
        meta_path = os.path.join(backup_dir, file.filename + ".meta.json")
        with open(meta_path, "w") as f:
            f.write(str(file.file_metadata))
    db.close()

if __name__ == "__main__":
    backup_all_files()
