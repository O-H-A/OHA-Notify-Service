import asyncio

import nest_asyncio
import py_eureka_client.eureka_client as eureka_client
from fastapi import FastAPI, APIRouter, HTTPException

from app.config.env import env
from app.config.handler.exception_handler import custom_exception_handler
from app.router import notify_router

nest_asyncio.apply()  # asyncio loop 문제 해결

app = FastAPI(docs_url='/api/notify/docs', openapi_url='/api/notify/openapi.json')  # swagger 경로

app.add_exception_handler(HTTPException, custom_exception_handler)  # 커스텀 예외 핸들러
app.add_exception_handler(Exception, custom_exception_handler)  # 커스텀 예외 핸들러

router = APIRouter()
app.include_router(notify_router.router, prefix="/api/notify")


async def init_eureka():  # eureka client 등록
    eureka_client.init(eureka_server=env.EUREKA_SERVER,
                       app_name=env.EUREKA_APP_NAME,
                       instance_host=env.HOST,
                       instance_port=int(env.PORT))


asyncio.run(init_eureka())
