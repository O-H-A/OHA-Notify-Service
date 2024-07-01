from pydantic import BaseModel


class BaseResponse(BaseModel):
    statusCode: int
    message: str
