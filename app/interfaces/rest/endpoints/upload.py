from fastapi import APIRouter, UploadFile, File

from app.domain.upload.entity import ImageRes
from app.shared.cloudianry import create_upload_file
from app.shared.decorator import response_decorator
from app.shared.validate_image import validate_image

router = APIRouter()


@router.post(
    "/image",
    response_model=ImageRes,
)
@response_decorator()
def create_image(
        image: UploadFile = File(...),
):
    validate_image(image)
    url = create_upload_file(image)
    return {"url": url}
