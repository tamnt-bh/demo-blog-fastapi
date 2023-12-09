from fastapi import UploadFile, HTTPException


def validate_image(image: UploadFile) -> None:
    if image.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=422,
            detail="Must be an image file.",
        )
