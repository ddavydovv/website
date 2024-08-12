from typing import Optional
from pydantic import BaseModel, validator


class UserCreate(BaseModel):
    user_nickname: str
    user_password: str


class User(UserCreate):
    user_role: str
    user_uuid: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_nickname: str
    user_role: str


class Item(BaseModel):
    item_author_uuid: str
    item_author_nickname: str
    item_category: str
    item_title: str
    item_caption: str


class ItemDetails(BaseModel):
    item_uuid: str


class ItemsAdvertising(BaseModel):
    item_author_nickname: Optional[str] = None
    item_category: Optional[str] = None
    item_title: Optional[str] = None
    caption_item: Optional[str] = None


class ItemComments(BaseModel):
    from_item_item_uuid: str
    item_comment_author_nickname: str
    item_comment_rating: int
    item_comment_title: str
    item_comment_caption: str

    @validator('item_comment_rating')
    @classmethod
    def validate_item_comment_rating(cls, value):
        if not 1 <= value <= 5:
            raise ValueError("item_comment_rating должен быть от 1 до 5.")
        return value


class ItemComplaints(BaseModel):
    complaints_item_type: str
    complaints_item_author_uuid: str
    complaints_item_author_nickname: str


class ItemComplaintsChangeStatus(BaseModel):
    complaints_item_uuid: str
    complaints_item_status: str



class Delete(BaseModel):
    uuid: str