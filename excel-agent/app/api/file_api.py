from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import FileResponse

from app.core.config import settings
from app.services.file_service import save_upload

router = APIRouter(prefix="/api/files", tags=["files"])


@router.post("/upload")
async def upload_file(file: UploadFile):
    if not file.filename.endswith((".xlsx", ".xls", ".csv")):
        raise HTTPException(status_code=400, detail="Only Excel/CSV files are supported")

    saved_path = await save_upload(file)
    return {"filename": file.filename, "path": saved_path}


@router.get("/download/{filename}")
async def download_file(filename: str):
    # Search in outputs/ first, then uploads/
    for dir_path in [settings.outputs_dir, settings.uploads_dir]:
        filepath = dir_path / filename
        if filepath.exists() and filepath.is_file():
            return FileResponse(
                path=str(filepath),
                filename=filename,
                media_type="application/octet-stream",
            )

    raise HTTPException(status_code=404, detail=f"File '{filename}' not found")