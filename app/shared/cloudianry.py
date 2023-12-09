import cloudinary
import cloudinary.uploader
from fastapi import File, UploadFile, HTTPException

from app.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)


def create_upload_file(file: UploadFile = File(...)):
    try:
        upload_result = cloudinary.uploader.upload(file.file)
        url = upload_result['secure_url']
        return url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
