from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from app.config.response.base_dto import BaseResponse


async def custom_exception_handler(request, exc):
    if isinstance(exc, HTTPException):
        response_body = jsonable_encoder(BaseResponse(statusCode=exc.status_code, message=exc.detail))
        return JSONResponse(content=response_body, status_code=exc.status_code)
    elif isinstance(exc, Exception):
        response_body = jsonable_encoder(BaseResponse(statusCode=500, message=str(exc)))
        return JSONResponse(content=response_body, status_code=500)
