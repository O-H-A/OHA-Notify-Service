import asyncio

from fastapi import APIRouter, Depends, Header, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.response.base_dto import BaseResponse
from app.database.database import get_db
from app.dto.notification_search import NotificationSearchResponse
from app.service import notify_service

router = APIRouter()

auth_scheme = HTTPBearer()


@router.get("", summary="알림 조회"
    , description="**statusCode:**\n" +
                  "- 200: 알림 있음\n" +
                  "- 404: 알림 없음\n" +
                  "- 500: 서버 오류"
    , response_model=NotificationSearchResponse, tags=["Notify"])
async def search(x_user_id: int = Header(include_in_schema=False)
                 , offset: int = Query(default=0)
                 , limit: int = Query(default=10, ge=1, le=50)
                 , token: HTTPAuthorizationCredentials = Depends(auth_scheme)
                 , db: AsyncSession = Depends(get_db)):
    return await notify_service.search_notification(x_user_id, offset, limit, token, db)


@router.get("/check", summary="새 알림 확인"
    , description="**statusCode:**\n" +
                  "- 200: 새 알림 있음\n" +
                  "- 404: 새 알림 없음\n" +
                  "- 500: 서버 오류"
    , response_model=BaseResponse, tags=["Notify"])
async def check(x_user_id: int = Header(include_in_schema=False)
          , token: HTTPAuthorizationCredentials = Depends(auth_scheme)
          , db: AsyncSession = Depends(get_db)):
    return await notify_service.check_new_notification(x_user_id, token, db)


asyncio.create_task(notify_service.consume())
