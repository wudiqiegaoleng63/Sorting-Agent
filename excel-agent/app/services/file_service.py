from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.utils.path_utils import safe_path


async def save_upload(file: UploadFile) -> str:
    """Save an uploaded file to the uploads directory. Returns the relative path."""
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)

    dest = settings.uploads_dir / file.filename
    # Ensure no path traversal
    safe_path(file.filename, settings.uploads_dir)

    content = await file.read()
    dest.write_bytes(content)

    return f"uploads/{file.filename}"
