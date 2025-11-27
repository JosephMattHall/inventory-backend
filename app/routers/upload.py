from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
from uuid import uuid4

router = APIRouter()

MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # validate extension
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        raise HTTPException(400, "Invalid image format")

    # new filename
    filename = f"{uuid4()}.{ext}"
    filepath = os.path.join(MEDIA_DIR, filename)

    # save file
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "url": f"/media/{filename}"
    }
