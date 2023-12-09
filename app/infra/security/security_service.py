from datetime import timedelta, datetime
from typing import Optional

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.domain.auth.entity import TokenData
from app.domain.user.entity import UserInDB
from app.infra.database.models.user import UserModel
from app.infra.user.user_repository import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_STR}/auth/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

forbidden_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Do not have permission",
)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def verify_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email, id=payload.get("id"))
        return token_data
    except JWTError:
        raise credentials_exception


def get_password_hash(password):
    return pwd_context.hash(password)


def get_current_user(
        token: str = Depends(oauth2_scheme),
        user_repository: UserRepository = Depends(UserRepository),
) -> UserModel:
    token_data = verify_token(token=token)
    user: UserModel = user_repository.get_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


def get_current_admin(
        user: UserModel = Depends(get_current_user),
) -> UserModel:
    current_user = UserInDB.model_validate(user)
    if not current_user.is_admin():
        raise forbidden_exception
    return user


def create_access_token(data: TokenData, expires_delta: timedelta = None) -> str:
    to_encode = data.model_dump()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    if isinstance(encoded_jwt, str):
        return encoded_jwt
    else:
        return encoded_jwt.decode("utf-8")
