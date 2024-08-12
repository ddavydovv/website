import json
import uuid
from sqlalchemy.orm import selectinload
import redis.asyncio as redis
from schemas import (Item, ItemComplaints, ItemComplaintsChangeStatus, ItemsAdvertising, ItemDetails, ItemComments,
                     UserCreate)
from db import async_session, ITEMS, ITEM_COMMENTS, COMPLAINTS_ITEM, USERS
from sqlalchemy import func, select, delete
from dotenv import load_dotenv
import os

load_dotenv()

REDIS = os.getenv("REDIS")
redis_client = redis.from_url(REDIS)


class SqlRegistration:
    @classmethod
    async def sql_register_user(cls, user: UserCreate):
        async with async_session() as session:
            try:
                db_user = USERS(user_uuid=str(uuid.uuid4()), user_nickname=user.user_nickname,
                                user_password=user.user_password)
                session.add(db_user)
                await session.commit()
                await session.refresh(db_user)
            except Exception as e:
                db_user = f'Произошла ошибка: {e}'
            return db_user

    @classmethod
    async def sql_get_token(cls, form_data):
        async with async_session() as session:
            try:
                user = await session.execute(select(USERS).filter_by(user_nickname=form_data.username))
                user_scalar = user.scalar()
            except Exception as e:
                user_scalar = f'Произошла ошибка: {e}'
            return user_scalar


class SqlItems:
    @classmethod
    async def sql_add_item(cls, data: Item):
        async with async_session() as session:
            try:
                task_dict = data.model_dump()
                print(f'TASK DICT: {task_dict}')
                response = ITEMS(item_uuid=str(uuid.uuid4()), item_author_uuid=task_dict['item_author_uuid'],
                    item_author_nickname=task_dict['item_author_nickname'], item_category=task_dict['item_category'],
                    item_title=task_dict['item_title'], item_caption=task_dict['item_caption'])
                session.add(response)
                await session.flush()
                await session.commit()
            except Exception as e:
                response = f'Произошла ошибка: {e}'
            return response

    @classmethod
    async def sql_delete_item(cls, data: Item):
        async with async_session() as session:
            try:
                task_dict = data.model_dump()
                print(f'TASK DICT: {task_dict}')
                cache_key = f"item_details:{task_dict['uuid']}"
                cached_data = await redis_client.get(cache_key)
                if cached_data:
                    await redis_client.delete(cache_key)
                item = await session.execute(select(ITEMS).filter_by(item_uuid=task_dict['uuid']))
                item_scalar = item.scalar()
                if item_scalar:
                    await session.execute(
                        delete(ITEM_COMMENTS).where(ITEM_COMMENTS.from_item_item_uuid == task_dict['uuid']))
                    await session.delete(item_scalar)
                    await session.commit()
                    response = f'Статья и все связанные комментарии успешно удалены!'
                else:
                    response = 'Элемент не найден!'

            except Exception as e:
                response = f'Произошла ошибка: {e}'
            return response

    @classmethod
    async def sql_get_all_items(cls, data: ItemsAdvertising, page: int, limit: int):
        async with async_session() as session:
            item_dict = data.model_dump()
            filters = {key: value for key, value in item_dict.items() if value is not None}

            total_query = await session.execute(select(func.count()).select_from(ITEMS).filter_by(**filters))
            total_count = total_query.scalar()

            query = select(ITEMS).filter_by(**filters).offset((page - 1) * limit).limit(limit)
            result = await session.execute(query)
            items = result.scalars().all()

            data_dict = []
            for item in items:
                data_dict.append(
                    {"item_uuid": item.item_uuid, "item_title": item.item_title, "item_caption": item.item_caption,
                        "item_category": item.item_category, "item_author_nickname": item.item_author_nickname,
                        "item_create_date": item.item_create_date.isoformat()})

            return {"items": data_dict, "total_count": total_count, "current_page": page,
                "total_pages": (total_count + limit - 1) // limit}

    @classmethod
    async def sql_get_item_details(cls, data: ItemDetails):
        async with async_session() as session:
            try:
                task_dict = data.model_dump()
                print(f'TASK DICT: {task_dict}')
                cache_key = f"item_details:{task_dict['item_uuid']}"
                cached_data = await redis_client.get(cache_key)
                if cached_data:
                    print(f'КЭШ: {json.loads(cached_data)}')
                    return json.loads(cached_data), 'ИСПОЛЬЗОВАЛИ КЭШ'
                else:
                    response = {}
                    item = await session.execute(
                        select(ITEMS).filter_by(item_uuid=task_dict['item_uuid']).options(selectinload(ITEMS.comments)))
                    details = item.scalar()
                    response['item_uuid'] = details.item_uuid
                    response['item_author_uuid'] = details.item_author_uuid
                    response['item_author_nickname'] = details.item_author_nickname
                    response['item_category'] = details.item_category
                    response['item_title'] = details.item_title
                    response['item_caption'] = details.item_caption
                    response['item_create_date'] = details.item_create_date.strftime('%Y-%m-%d %H:%M:%S')
                    response['item_last_update_date'] = details.item_last_update_date.strftime('%Y-%m-%d %H:%M:%S')
                    response['comments'] = []
                    n = 10
                    for comment in details.comments:
                        response['comments'].append({'item_comment_uuid': comment.item_comment_uuid,
                            "item_comment_author_nickname": comment.item_comment_author_nickname,
                            "item_comment_rating": comment.item_comment_rating,
                            "item_comment_title": comment.item_comment_title,
                            "item_comment_caption": comment.item_comment_caption,
                            "item_comment_create_date": comment.item_comment_create_date.strftime('%Y-%m-%d %H:%M:%S'),
                            "item_comment_last_update_date": comment.item_comment_last_update_date.strftime(
                                '%Y-%m-%d %H:%M:%S'), "item_comment_likes": comment.item_comment_likes,
                            "item_comment_dislikes": comment.item_comment_dislikes,
                            "item_comment_status": comment.item_comment_status})
                    await redis_client.set(cache_key, json.dumps(response), ex=1000)
            except Exception as e:
                response = f'Произошла ошибка: {e}'
            return response, 'ИСПОЛЬЗОВАЛИ ЗАПРОС К БД'


class SqlItemComments:

    @classmethod
    async def sql_add_item_comments(cls, data: ItemComments):
        async with async_session() as session:
            try:
                task_dict = data.model_dump()
                print(f'TASK DICT: {task_dict}')
                cache_key = f"item_details:{task_dict['from_item_item_uuid']}"
                cached_data = await redis_client.get(cache_key)
                if cached_data:
                    await redis_client.delete(cache_key)
                else:
                    pass
                response = ITEM_COMMENTS(item_comment_uuid=str(uuid.uuid4()),
                    from_item_item_uuid=task_dict['from_item_item_uuid'],
                    item_comment_author_nickname=task_dict['item_comment_author_nickname'],
                    item_comment_rating=task_dict['item_comment_rating'],
                    item_comment_title=task_dict['item_comment_title'],
                    item_comment_caption=task_dict['item_comment_caption'])
                session.add(response)
                await session.flush()
                await session.commit()
            except Exception as e:
                response = f'Произошла ошибка: {e}'
            return response

    @classmethod
    async def sql_delete_item_comment(cls, data: Item):
        async with async_session() as session:
            try:
                task_dict = data.model_dump()
                print(f'TASK DICT: {task_dict}')
                cache_key = f"item_details:{task_dict['from_item_item_uuid']}"
                cached_data = await redis_client.get(cache_key)
                if cached_data:
                    await redis_client.delete(cache_key)
                else:
                    pass
                comment = await session.execute(select(ITEM_COMMENTS).filter_by(item_comment_uuid=task_dict['uuid']))
                comment_scalar = comment.scalar()
                await session.delete(comment_scalar)
                await session.commit()
                response = f'Статья успешно удалена!'
            except Exception as e:
                response = f'Произошла ошибка: {e}'
            return response


class SqlItemComplaints:

    @classmethod
    async def sql_add_complaint(cls, data: ItemComplaints):
        async with async_session() as session:
            try:
                task_dict = data.model_dump()
                print(f'TASK DICT: {task_dict}')
                complaint = COMPLAINTS_ITEM(complaints_item_uuid=str(uuid.uuid4()),
                    complaints_item_type=task_dict['complaints_item_type'],
                    complaints_item_author_uuid=task_dict['complaints_item_author_uuid'],
                    complaints_item_author_nickname=task_dict['complaints_item_author_nickname'])
                session.add(complaint)
                await session.flush()
                await session.commit()
            except Exception as e:
                response = f'Произошла ошибка: {e}'
            return response

    @classmethod
    async def sql_item_complaint_change_status(cls, data: ItemComplaintsChangeStatus):
        async with async_session() as session:
            try:
                task_dict = data.model_dump()
                print(f'TASK DICT: {task_dict}')
                complaint = await session.execute(
                    select(COMPLAINTS_ITEM).filter_by(complaints_item_uuid=task_dict['uuid']))
                complaint_scalar = complaint.scalar()
                complaint_scalar.complaints_item_status = task_dict['complaints_item_status']
                await session.flush()
                await session.commit()
                response = f'Статья успешно удалена!'
            except Exception as e:
                response = f'Произошла ошибка: {e}'
            return response