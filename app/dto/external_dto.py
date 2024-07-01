from typing import Optional

from pydantic import BaseModel


class ExternalUser(BaseModel):
    userId: int
    name: Optional[str] = None
    profileUrl: Optional[str] = None


class ExternalPost(BaseModel):
    postId: int
    userId: int
    thumbnailUrl: Optional[str] = None
    mediaType: Optional[str] = '사진'


class ExternalDiary(BaseModel):
    diaryId: int
    userId: int
    thumbnailUrl: Optional[str] = None
