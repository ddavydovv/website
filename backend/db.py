from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async_engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)
Base = declarative_base()


class USERS(Base):
    __tablename__ = 'users'

    user_uuid = Column(String, primary_key=True, index=True, comment='uuid пользователя')
    user_role = Column(String, default='Обычный', unique=False, index=True)
    user_nickname = Column(String, unique=True, index=True)
    user_password = Column(String, unique=False, index=True)
    user_create_date = Column(DateTime, default=datetime.now(), unique=False, index=True)
    user_items_count = Column(Integer, default=0, unique=False, index=True)
    user_rating = Column(Integer, default=0, unique=False, index=True)
    user_block_status = Column(String, default='Активный', unique=False, index=True)


class ITEMS(Base):
    __tablename__ = 'items'

    item_uuid = Column(String, primary_key=True, index=True)
    item_author_uuid = Column(String, unique=False, index=True)
    item_author_nickname = Column(String, unique=False, index=True)
    item_category = Column(String, unique=False, index=True)
    item_title = Column(String, unique=False, index=True)
    item_caption = Column(String, unique=False, index=True)
    item_create_date = Column(DateTime, default=datetime.now(), unique=False, index=True)
    item_last_update_date = Column(DateTime, default=datetime.now(), unique=False, index=True)
    comments = relationship("ITEM_COMMENTS", back_populates="item")


class ITEM_COMMENTS(Base):
    __tablename__ = 'item_comments'

    item_comment_uuid = Column(String, primary_key=True, index=True)
    from_item_item_uuid = Column(String, ForeignKey('items.item_uuid'), unique=False, index=True)
    item_comment_author_nickname = Column(String, unique=False, index=True)
    item_comment_rating = Column(Integer, unique=False, index=True)
    item_comment_title = Column(String, unique=False, index=True)
    item_comment_caption = Column(String, unique=False, index=True)
    item_comment_create_date = Column(DateTime, default=datetime.now(), unique=False, index=True)
    item_comment_last_update_date = Column(DateTime, default=datetime.now(), unique=False, index=True)
    item_comment_likes = Column(Integer, default=0, unique=False, index=True)
    item_comment_dislikes = Column(Integer, default=0, unique=False, index=True)
    item_comment_status = Column(String, default='Опубликован', unique=False, index=True)
    item = relationship("ITEMS", back_populates="comments")


class COMPLAINTS_ITEM(Base):
    __tablename__ = 'complaints_item'

    complaints_item_uuid = Column(String, primary_key=True, index=True)
    complaints_item_type = Column(String, unique=False, index=True)
    complaints_item_author_uuid = Column(Integer, unique=False, index=True)
    complaints_item_author_nickname = Column(String, unique=False, index=True)
    complaints_item_create_date = Column(DateTime, default=datetime.now(), unique=False, index=True)
    complaints_item_responsible_administrator_uuid = Column(String, unique=False, index=True)
    complaints_item_responsible_administrator_nickname = Column(String, unique=False, index=True)
    complaints_item_date_of_review = Column(DateTime, unique=False, index=True)
    complaints_item_status = Column(Integer, default='На рассмотрении', unique=False, index=True)


async def create_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def delete_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)