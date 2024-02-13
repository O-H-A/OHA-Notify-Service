from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.env import DB_URL, DB_SCHEMA
import logging

SQLALCHEMY_DATABASE_URL = DB_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base(metadata=MetaData(schema=DB_SCHEMA))

Base.metadata.create_all(bind=engine)

# SQLAlchemy ORM 쿼리 로깅을 위한 로거 생성
sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_logger.setLevel(logging.INFO)

# SQLAlchemy 엔진에 로거 추가
engine_logger = logging.getLogger("sqlalchemy")
engine_logger.addHandler(logging.StreamHandler())


def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
