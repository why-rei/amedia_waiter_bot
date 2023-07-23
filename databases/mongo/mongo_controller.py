import os
from datetime import datetime
from typing import List, Type

from motor import motor_asyncio
from motor.motor_asyncio import AsyncIOMotorCursor
from bson import ObjectId

client = motor_asyncio.AsyncIOMotorClient('localhost', 27017)
db = client.mongo
collection = db.notice


class MongoNotice:
    @staticmethod
    async def _check_notice(anime_id: int, anime_seria: str) -> int:
        check = await collection.count_documents({'anime_id': anime_id, 'anime_seria': anime_seria})
        return check

    async def create_notice(self, notice_id: int, anime_id: int, anime_seria: str, users: List[int]) -> None:
        check = await self._check_notice(anime_id=anime_id, anime_seria=anime_seria)
        if not check:
            await collection.insert_one(
                {
                    'date_time': datetime.now(),
                    'notice_id': notice_id,
                    'anime_id': anime_id,
                    'anime_seria': anime_seria,
                    'users': [{'user_id': x, 'got': 0} for x in users]
                }
            )

    @staticmethod
    async def get_notices() -> Type[AsyncIOMotorCursor]:
        if collection.count_documents({}):
            notices = collection.find({})
            return notices

    @staticmethod
    async def set_user_got(_id: str, user_id: int, user_got: int = 1) -> None:
        await collection.update_one({'_id': ObjectId(_id), 'users.user_id': user_id},
                                    {'$set': {'users.$.got': user_got}})

    @staticmethod
    async def delete_notice(_id: str) -> None:
        got_check = await collection.find_one({'_id': _id, 'users.got': 0})
        if not got_check:
            await collection.delete_one({"_id": ObjectId(_id)})
