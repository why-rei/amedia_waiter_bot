import pprint
from datetime import datetime
from typing import List, Type, Tuple, Any

from motor import motor_asyncio
from motor.motor_asyncio import AsyncIOMotorCursor
from bson import ObjectId

CLIENT = motor_asyncio.AsyncIOMotorClient('localhost', 27017)
DB = CLIENT.mongo


class MongoAnimes:
    collection = DB.animes

    async def _check_anime(self, anime_id: int) -> int:
        check = await self.collection.count_documents({'anime_id': anime_id})
        return check

    async def add_anime(self, anime_id: int, anime_name: str) -> None:
        if not await self._check_anime(anime_id=anime_id):
            await self.collection.insert_one(
                {
                    'anime_id': anime_id,
                    'anime_name': anime_name
                }
            )

    async def find_animes(self, req: str) -> list[Any]:
        anime_items = []
        if req:
            async for item in self.collection.find({"anime_name": {"$regex": f'(?i:{req})'}}):
                anime_items.append((item['anime_id'], item['anime_name']))

        return anime_items


class MongoNotice:
    collection = DB.notice

    async def _check_notice(self, anime_id: int, anime_seria: str) -> int:
        check = await self.collection.count_documents({'anime_id': anime_id, 'anime_seria': anime_seria})
        return check

    async def create_notice(self, notice_id: int, anime_id: int, anime_seria: str, users: List[int]) -> None:
        check = await self._check_notice(anime_id=anime_id, anime_seria=anime_seria)
        if not check:
            await self.collection.insert_one(
                {
                    'date_time': datetime.now(),
                    'notice_id': notice_id,
                    'anime_id': anime_id,
                    'anime_seria': anime_seria,
                    'users': [{'user_id': x, 'got': 0} for x in users]
                }
            )

    async def get_notices(self) -> Type[AsyncIOMotorCursor]:
        if self.collection.count_documents({}):
            notices = self.collection.find({})
            return notices

    async def set_user_got(self, _id: str, user_id: int, user_got: int = 1) -> None:
        await self.collection.update_one({'_id': ObjectId(_id), 'users.user_id': user_id},
                                         {'$set': {'users.$.got': user_got}})

    async def delete_notice(self, _id: str) -> None:
        got_check = await self.collection.find_one({'_id': _id, 'users.got': 0})
        if not got_check:
            await self.collection.delete_one({"_id": ObjectId(_id)})
