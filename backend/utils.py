from datetime import timedelta, datetime
from typing import Optional
from starlette import status
from schemas import TokenData
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


# Функции для управления JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Авторизация пользователя
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Проверка прав доступа
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось верифицировать учетные данные", headers={"WWW-Authenticate": "Bearer"}, )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_nickname = payload.get("user_nickname")
        user_role = payload.get("user_role")
        if user_nickname is None:
            raise credentials_exception
        return TokenData(user_nickname=user_nickname, user_role=user_role)
    except jwt.PyJWTError:
        raise credentials_exception