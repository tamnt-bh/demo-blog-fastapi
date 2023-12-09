from fastapi import APIRouter

from app.interfaces.rest.endpoints import auth, post, user, upload

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(post.router, prefix="/post", tags=["Post"])
api_router.include_router(user.router, prefix="/user", tags=["User"])
api_router.include_router(upload.router, prefix="/upload", tags=["Upload"])
