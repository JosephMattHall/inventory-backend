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
    print(f"Received file: {file.filename}")
    if "." not in file.filename:
         raise HTTPException(400, "File has no extension")
         
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        raise HTTPException(400, f"Invalid image format: {ext}. Allowed: jpg, jpeg, png, webp")

    # new filename
    filename = f"{uuid4()}.{ext}"
    filepath = os.path.join(MEDIA_DIR, filename)

    # save file
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "url": f"/media/{filename}"
    }
