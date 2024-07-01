import logging
from asyncio import current_task

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_scoped_session, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config.env.env import DB_URL, DB_SCHEMA

SQLALCHEMY_DATABASE_URL = DB_URL.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

async_session = async_scoped_session(
    async_sessionmaker(
        bind=engine,
        class_=AsyncSession
    ),
    scopefunc=current_task,
)

Base = declarative_base(metadata=MetaData(schema=DB_SCHEMA))


# 비동기 데이터베이스 초기화 함수
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# SQLAlchemy ORM 쿼리 로깅을 위한 로거 생성
sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_logger.setLevel(logging.INFO)

# SQLAlchemy 엔진에 로거 추가
engine_logger = logging.getLogger("sqlalchemy")
engine_logger.addHandler(logging.StreamHandler())


async def get_db():
    db = None
    try:
        db = async_session()
        yield db
    finally:
        await db.close()
