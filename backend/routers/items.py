from typing import Annotated
from fastapi import Depends, Query, APIRouter
from starlette import status
from requests import SqlItems, SqlItemComments, SqlItemComplaints
from schemas import Item, ItemComments, Delete, ItemComplaintsChangeStatus, ItemsAdvertising, ItemDetails, TokenData
from fastapi import Body, HTTPException
from utils import get_current_user


items_router = APIRouter(tags=['Operations with items'])


# ЭНДПОИНТЫ СТАТЕЙ
@items_router.post("/item/add")
async def post_items(item: Annotated[Item, Depends(SqlItems.sql_add_item)] = Body(...)):
    return {"data": item}


@items_router.post("/item/delete")
async def post_items(item_payload: Delete = Body(), current_user: TokenData = Depends(get_current_user)):
    if current_user.user_role != "Администратор":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Доступ запрещен. Только администраторы могут удалять элементы.")
    else:
        result = await SqlItems.sql_delete_item(item_payload)
        return {"data": result}


@items_router.get("/items")
async def get_items(item_payload: Annotated[ItemsAdvertising, Depends()], page: int = Query(1, ge=1), limit: int = Query(10, gt=0)):
    data = await SqlItems.sql_get_all_items(item_payload, page, limit)
    return data


@items_router.post("/item/details")
async def post_items(item_payload: ItemDetails = Body()):
    data, notification = await SqlItems.sql_get_item_details(item_payload)
    print(f'NOTIFICATION: {notification}')
    return data


# ЭНДПОИНТЫ КОММЕНТАРИЕВ К СТАТЬЯМ
@items_router.post("/item/comment/add")
async def post_items(comment: Annotated[ItemComments, Depends(SqlItemComments.sql_add_item_comments)] = Body(...)):
    return {"data": comment}


@items_router.post("/item/comment/delete")
async def post_items(item_comments_payload: Delete = Body(), current_user: TokenData = Depends(get_current_user)):
    if current_user.user_role != "Администратор":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Доступ запрещен. Только администраторы могут удалять элементы.")
    else:
        result = await SqlItemComments.sql_delete_item_comment(item_comments_payload)
        return {"data": result}


# ЭНДПОИНТЫ ЖАЛОБ НА СТАТЬИ
@items_router.post("/item/complaint/add")
async def post_items(complaint: Annotated[Item, Depends(SqlItemComplaints.sql_add_complaint)] = Body(...)):
    return {"data": complaint}


@items_router.post("/item/complaint/delete")
async def post_items(item_comments_payload: ItemComplaintsChangeStatus = Body(), current_user: TokenData = Depends(get_current_user)):
    if current_user.user_role != "Администратор":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Доступ запрещен. Только администраторы могут удалять элементы.")
    else:
        input_result = await SqlItemComplaints.sql_item_complaint_change_status(item_comments_payload)
        return {"item_comments_payload": item_comments_payload, "input_result": input_result}