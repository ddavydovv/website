from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, items


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await db.delete_database()
    # await db.create_database()
    print('Запущено')
    yield
    print('Выключение')


app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware,
                       allow_origins=[
                           "http://localhost:5173",
                           "http://127.0.0.1:5173",
                           "http://localhost:3000"
                       ],
                       allow_credentials=True,
                       allow_methods=["*"],
                       allow_headers=["*"], )
app.include_router(auth.auth_router)
app.include_router(items.items_router)