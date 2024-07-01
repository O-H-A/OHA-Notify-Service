from typing import Optional

from pydantic import BaseModel

from app.config.response.base_dto import BaseResponse


class NotificationInsert(BaseModel):
    user_id: int
    type: str
    data: dict


class NotificationInsertResponse(BaseResponse):
    class NotificationInsertData(BaseModel):
        notification_id: int

    data: Optional[NotificationInsertData] = None

