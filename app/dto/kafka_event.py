from typing import Optional, List

from pydantic import BaseModel


class PostLikeEvent(BaseModel):
    user_id: int
    post_id: int
    like_user_id: int
    like_user_name: str
    media_type: str
    profile_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    fcm_token: Optional[str] = None


class DiaryLikeEvent(BaseModel):
    user_id: int
    diary_id: int
    like_user_id: int
    like_user_name: str
    profile_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    fcm_token: Optional[str] = None


class WeatherRegEvent(BaseModel):
    class UserInfo(BaseModel):
        user_id: int
        user_name: str
        fcm_token: Optional[str] = None
        profile_url: Optional[str] = None

    user_list: List[UserInfo]


class ReportEvent(BaseModel):
    report_id: int
    report_reason: str

    reporting_user_id: int
    reporting_user_name: Optional[str] = None
    reporting_user_profile_url: Optional[str] = None
    reporting_user_fcm_token: Optional[str] = None

    reported_user_id: int
    reported_user_name: Optional[str] = None
    reported_user_profile_url: Optional[str] = None
    reported_user_fcm_token: Optional[str] = None

    thumbnail_url: Optional[str] = None


class PostReportEvent(ReportEvent):  # 게시물 신고
    post_id: int


class DiaryReportEvent(ReportEvent):  # 다이어리 신고
    diary_id: int


class PostCommentEvent(BaseModel):
    user_id: int
    post_id: int
    comment_user_id: int
    comment_user_name: str
    comment_content: str
    profile_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    fcm_token: Optional[str] = None
