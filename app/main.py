from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.infra import database
from app.interfaces.rest.api import api_router

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'],
                   allow_headers=['*'], )


# app startup handler
@app.on_event("startup")
def startup():
    database.connect()


# app shutdown handler
@app.on_event("shutdown")
def shutdown():
    database.disconnect()


app.include_router(api_router, prefix=settings.API_STR)
