from typing import Optional

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="forbid")

    # mongodb
    MONGODB_HOST: str
    MONGODB_PORT: int
    MONGODB_DATABASE: str
    MONGODB_USERNAME: str
    MONGODB_PASSWORD: str
    MONGODB_EXPOSE_PORT: int

    API_STR: str
    PROJECT_NAME: str = "Demo Blog FastAPI"
    API_PORT: Optional[int] = 8000

    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE: int = 1
    SECRET_KEY: str = "secret"

    ENVIRONMENT: str


settings = Settings()
