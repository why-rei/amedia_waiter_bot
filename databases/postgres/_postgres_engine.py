from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from core.settings import POSTGRES_CONN

engine = create_async_engine(POSTGRES_CONN, pool_size=30, max_overflow=-1)

Async_Session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
