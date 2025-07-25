import os
from supabase import create_client, Client
from typing import Optional
import gzip
import tempfile
from cryptography.fernet import Fernet

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "files")
ENCRYPTION_KEY = os.getenv("FILE_ENCRYPTION_KEY")  # Should be a 32-byte base64 key

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ALLOWED_EXTENSIONS = {"pdf", "docx", "png", "jpg", "jpeg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def validate_file(file_path: str, allowed_extensions=ALLOWED_EXTENSIONS, max_size=MAX_FILE_SIZE):
    ext = os.path.splitext(file_path)[1][1:].lower()
    if ext not in allowed_extensions:
        raise ValueError(f"File type .{ext} is not allowed.")
    size = os.path.getsize(file_path)
    if size > max_size:
        raise ValueError(f"File size {size} exceeds max allowed {max_size} bytes.")
    return ext, size


def encrypt_and_compress(file_path: str, key: str) -> str:
    fernet = Fernet(key)
    with open(file_path, "rb") as f:
        data = f.read()
    compressed = gzip.compress(data)
    encrypted = fernet.encrypt(compressed)
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(encrypted)
    temp.close()
    return temp.name


def upload_file(file_path: str, dest_path: str, content_type: Optional[str] = None, encrypt: bool = True, compress: bool = True) -> dict:
    ext, size = validate_file(file_path)
    temp_path = file_path
    is_encrypted = False
    is_compressed = False
    if encrypt or compress:
        if not ENCRYPTION_KEY:
            raise ValueError("ENCRYPTION_KEY not set in environment.")
        temp_path = encrypt_and_compress(file_path, ENCRYPTION_KEY)
        is_encrypted = encrypt
        is_compressed = compress
    with open(temp_path, "rb") as f:
        res = supabase.storage().from_(SUPABASE_BUCKET).upload(dest_path, f, file_options={"content-type": content_type} if content_type else None)
    if temp_path != file_path:
        os.remove(temp_path)
    return {"result": res, "is_encrypted": is_encrypted, "is_compressed": is_compressed}


def download_file(dest_path: str, local_path: str) -> None:
    res = supabase.storage().from_(SUPABASE_BUCKET).download(dest_path)
    with open(local_path, "wb") as f:
        f.write(res)


def delete_file(dest_path: str) -> dict:
    res = supabase.storage().from_(SUPABASE_BUCKET).remove([dest_path])
    return res


def generate_signed_url(dest_path: str, expires_in: int = 3600) -> str:
    res = supabase.storage().from_(SUPABASE_BUCKET).create_signed_url(dest_path, expires_in)
    return res.get("signedURL")
