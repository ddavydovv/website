from fastapi import Depends, APIRouter
from starlette import status
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from requests import SqlRegistration
from schemas import UserCreate, Token
from utils import create_access_token

auth_router = APIRouter(tags=['Registration / Auth'])


# Регистрация пользователя
@auth_router.post("/register", response_model=UserCreate)
async def register(user: UserCreate):
    result = await SqlRegistration.sql_register_user(user)
    return result


@auth_router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await SqlRegistration.sql_get_token(form_data)
    if not user or user.user_password != form_data.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Неверные учетные данные",
                            headers={"WWW-Authenticate": "Bearer"})
    access_token = create_access_token(data={"user_nickname": user.user_nickname, "user_role": user.user_role})
    return {"access_token": access_token, "token_type": "bearer"}