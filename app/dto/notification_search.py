from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.config.response.base_dto import BaseResponse


class NotificationSearchResponse(BaseResponse):
    class NotificationSearchData(BaseModel):
        notification_id: int
        user_id: int
        notification_code: str
        message: Optional[List[dict]] = None
        is_read: bool
        entry_id: Optional[int] = None
        entry_type: Optional[str] = None
        reg_dtm: datetime
        thumbnail_url: Optional[str] = None
        profile_url: Optional[str] = None

    data: Optional[List[NotificationSearchData]] = None
