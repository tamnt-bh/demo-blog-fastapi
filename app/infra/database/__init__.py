from mongoengine import connect as mongo_engine_connect, disconnect_all

from app.config import settings


def connect() -> None:
    if settings.ENVIRONMENT == "testing":
        return mongo_engine_connect(settings.MONGODB_DATABASE, host=settings.MONGODB_HOST, port=settings.MONGODB_PORT)
    else:
        return mongo_engine_connect(
            settings.MONGODB_DATABASE,
            host=settings.MONGODB_HOST,
            port=settings.MONGODB_PORT,
            username=settings.MONGODB_USERNAME,
            password=settings.MONGODB_PASSWORD,
            authentication_source=settings.MONGODB_DATABASE,
            alias="default",
        )


def disconnect() -> None:
    disconnect_all()
