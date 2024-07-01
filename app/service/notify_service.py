import asyncio
import logging

import aiohttp
from aiokafka import AIOKafkaConsumer
from fastapi import status, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import func, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.kafka.kafka_config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_CONSUMER_GROUP, loop, KAFKA_AUTO_OFFSET_RESET, \
    KAFKA_TOPICS
from app.config.response.base_dto import BaseResponse
from app.database.database import async_session
from app.dto.kafka_event import PostLikeEvent, DiaryLikeEvent, WeatherRegEvent, PostCommentEvent, PostReportEvent, \
    DiaryReportEvent
from app.dto.notification_search import NotificationSearchResponse
from app.model.models import Notification
from app.service.external_api_service import get_external_post_list, get_external_user_list, get_external_diary_list

# 로그 설정
logging.basicConfig(level=logging.INFO)  # 레벨 설정 (DEBUG, INFO, WARNING, ERROR, CRITICAL)


async def search_notification(user_id: int,
                              offset: int,
                              limit: int,
                              token: HTTPAuthorizationCredentials,
                              db: AsyncSession):
    result = await db.execute(
        select(Notification)
        .filter(Notification.user_id == user_id, Notification.is_del == False)
        .order_by(desc(Notification.reg_dtm))
        .offset(offset)
        .limit(limit)
    )
    notification_list = result.scalars().all()

    if not notification_list:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "알림이 없습니다.")
    else:
        await set_message(token.credentials, notification_list)

        data_list = list()
        for n in notification_list:
            notification_dict = n.__dict__
            data_list.append(NotificationSearchResponse.NotificationSearchData(**notification_dict))

        response = NotificationSearchResponse(statusCode=status.HTTP_200_OK, message="Success", data=data_list)

        for n in notification_list:
            n.is_read = True

        await db.commit()

    return response


async def check_new_notification(user_id: int, token: HTTPAuthorizationCredentials, db: AsyncSession):
    count = await db.execute(
        select(func.count(Notification.notification_id))
        .filter(Notification.user_id == user_id,
                Notification.is_read == False,
                Notification.is_del == False)
    )

    count = count.scalars().first()

    if count:
        response = BaseResponse(statusCode=status.HTTP_200_OK, message="새 알림이 있습니다.")
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "새 알림이 없습니다.")

    return response


async def set_message(token: str, notification_list: list[Notification]):
    # 일괄 조회 데이터
    user_ids = set()
    post_ids = set()
    diary_ids = set()

    # 알림 구분
    post_like_list = list()
    diary_like_list = list()
    weather_reg_list = list()
    post_reporting_list = list()
    post_reported_list = list()
    dairy_reporting_list = list()
    dairy_reported_list = list()
    post_comment_list = list()

    for n in notification_list:
        if n.notification_code == "NOTI001":  # 게시글 좋아요
            user_ids.add(n.data['like_user_id'])
            post_ids.add(n.data['post_id'])
            post_like_list.append(n)
        elif n.notification_code == "NOTI002":  # 다이어리 좋아요
            user_ids.add(n.data['like_user_id'])
            diary_ids.add(n.data['diary_id'])
            diary_like_list.append(n)
        elif n.notification_code == "NOTI003":  # 날씨 정보 등록
            weather_reg_list.append(n)
            user_ids.add(n.user_id)
        elif n.notification_code == "NOTI004":  # 게시물 신고한 유저
            user_ids.add(n.user_id)
            post_reporting_list.append(n)
        elif n.notification_code == "NOTI005":  # 게시물 신고 당한 유저
            user_ids.add(n.user_id)
            post_reported_list.append(n)
        elif n.notification_code == "NOTI006":  # 다이어리 신고한 유저
            user_ids.add(n.user_id)
            dairy_reporting_list.append(n)
        elif n.notification_code == "NOTI007":  # 다이어리 신고 당한 유저
            user_ids.add(n.user_id)
            dairy_reported_list.append(n)
        elif n.notification_code == "NOTI008":  # 게시물 댓글
            user_ids.add(n.data['comment_user_id'])
            post_ids.add(n.data['post_id'])
            post_comment_list.append(n)

    user_dict, post_dict, diary_dict = await gather_search_result(token, user_ids, post_ids, diary_ids)

    for like in post_like_list:
        like_user = user_dict.get(like.data.get("like_user_id"))
        like_post = post_dict.get(like.data.get("post_id"))

        like.profile_url = like_user.profileUrl
        like.message = [
            {"text": like_user.name, "type": "bold"}
            , {"text": f"님이 회원님의 {like_post.mediaType}을 좋아합니다.", "type": "plain"}
        ]
        like.thumbnail_url = like_post.thumbnailUrl
        like.entry_id = like_post.postId
        like.entry_type = 'post'

    for like in diary_like_list:
        like_user = user_dict.get(like.data.get("like_user_id"))
        like_diary = diary_dict.get(like.data.get("diary_id"))

        like.profile_url = like_user.profileUrl
        like.message = [
            {"text": like_user.name, "type": "bold"}
            , {"text": "님이 회원님의 일기를 좋아합니다.", "type": "plain"}
        ]

        like.thumbnail_url = like_diary.thumbnailUrl
        like.entry_id = like_diary.diaryId
        like.entry_type = 'diary'

    for w in weather_reg_list:
        weather_user = user_dict.get(w.user_id)
        w.profile_url = weather_user.profileUrl

        w.message = [
            {"text": f"{weather_user.name}", "type": "bold"}
            , {"text": "님이 계신 곳의 날씨 정보가 궁금해요! 현재 날씨 정보를 공유해 주세요.", "type": "plain"}
        ]

    for r in post_reporting_list:
        reporting_user = user_dict.get(r.user_id)
        r.profile_url = reporting_user.profileUrl
        r.message = [
            {"text": f"{reporting_user.name}", "type": "bold"}
            , {"text": f"님이 신고하신 {r.data.get("report_reason")}이 삭제 처리 되었습니다.", "type": "plain"}
        ]

    for r in post_reported_list:
        reported_user = user_dict.get(r.user_id)
        r.profile_url = reported_user.profileUrl
        r.message = [
            {"text": f"{r.data.get("report_reason")}로 신고가 접수되어 검토 후 게시물이 삭제 처리 되었습니다.", "type": "plain"}
        ]

    for r in dairy_reporting_list:
        reporting_user = user_dict.get(r.user_id)
        r.profile_url = reporting_user.profileUrl
        r.message = [
            {"text": f"{reporting_user.name}", "type": "bold"}
            , {"text": f"님이 신고하신 {r.data.get("report_reason")}이 삭제 처리 되었습니다.", "type": "plain"}
        ]

    for r in dairy_reported_list:
        reported_user = user_dict.get(r.user_id)
        r.profile_url = reported_user.profileUrl
        r.message = [
            {"text": f"{r.data.get("report_reason")}로 신고가 접수되어 검토 후 게시물이 삭제 처리 되었습니다.", "type": "plain"}
        ]

    for c in post_comment_list:
        comment_user = user_dict.get(c.data.get("comment_user_id"))
        comment_post = post_dict.get(c.data.get("post_id"))

        c.profile_url = comment_user.profileUrl
        c.message = [
            {"text": comment_user.name, "type": "bold"}
            , {"text": f"님이 댓글을 남겼습니다.", "type": "plain"}
        ]
        c.thumbnail_url = comment_post.thumbnailUrl
        c.entry_id = comment_post.postId
        c.entry_type = "post"


async def gather_search_result(token, user_ids, post_ids, diary_ids):
    async with aiohttp.ClientSession() as session:
        user_list, post_list, diary_list = await asyncio.gather(
            get_external_user_list(session, token, user_ids),
            get_external_post_list(session, token, post_ids),
            get_external_diary_list(session, token, diary_ids)
        )

        user_dict = {item.userId: item for item in user_list}
        post_dict = {item.postId: item for item in post_list}
        diary_dict = {item.diaryId: item for item in diary_list}

        return user_dict, post_dict, diary_dict


async def consume():
    consumer = AIOKafkaConsumer(*KAFKA_TOPICS, loop=loop,
                                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, group_id=KAFKA_CONSUMER_GROUP
                                , auto_offset_reset=KAFKA_AUTO_OFFSET_RESET)
    await consumer.start()
    try:
        async for msg in consumer:
            topic = msg.topic
            decoded_msg = msg.value.decode('utf-8')

            try:
                notification_list, push_list = get_notification_data(topic, decoded_msg)

                print("Received message from topic:", msg.topic)
                print("Received message: ", decoded_msg)

                async with async_session() as db:
                    await insert_notification(notification_list, db)
                await send_push_notification(push_list)

            except Exception as e:
                print(e)

    finally:
        await consumer.stop()


def get_notification_data(topic: str, decoded_msg: str):
    notification_list = list()
    push_list = list()

    if topic == KAFKA_TOPICS[0]:  # 게시물 좋아요
        model = PostLikeEvent.parse_raw(decoded_msg)
        notification = Notification(user_id=model.user_id, notification_code="NOTI001"
                                    , data={"like_user_id": model.like_user_id, "post_id": model.post_id})
        notification_list.append(notification)

        if model.fcm_token:
            push_data = {
                "title": "오하늘"
                , "msg": f"{model.like_user_name}님이 회원님의 {model.media_type}을 좋아합니다."
                , "token": model.fcm_token
                , "image_url": model.profile_url
            }
            push_list.append(push_data)

    elif topic == KAFKA_TOPICS[1]:  # 다이어리 좋아요
        model = DiaryLikeEvent.parse_raw(decoded_msg)
        notification = Notification(user_id=model.user_id, notification_code="NOTI002"
                                    , data={"like_user_id": model.like_user_id, "diary_id": model.diary_id})
        notification_list.append(notification)

        if model.fcm_token:
            push_data = {
                "title": "오하늘"
                , "msg": f"{model.like_user_name}님이 회원님의 일기를 좋아합니다."
                , "token": model.fcm_token
                , "image_url": model.profile_url
            }
            push_list.append(push_data)

    elif topic == KAFKA_TOPICS[2]:  # 날씨 등록
        model = WeatherRegEvent.parse_raw(decoded_msg)

        for user in model.user_list:
            notification = Notification(user_id=user.user_id, notification_code="NOTI003")
            notification_list.append(notification)

            if user.fcm_token:
                push_data = {
                    "title": "오하늘"
                    , "msg": f"{user.user_name}님이 계신 곳의 날씨 정보가 궁금해요! 현재 날씨 정보를 공유해 주세요."
                    , "token": user.fcm_token
                    , "image_url": user.profile_url
                }
                push_list.append(push_data)

    elif topic == KAFKA_TOPICS[3]:  # 게시물 신고
        model = PostReportEvent.parse_raw(decoded_msg)

        # 신고자
        notification = Notification(user_id=model.reporting_user_id, notification_code="NOTI004"
                                    , data={"report_id": model.report_id
                , "post_id": model.post_id
                , "report_reason": model.report_reason})
        notification_list.append(notification)

        if model.reporting_user_fcm_token:
            push_list.append({
                "title": "오하늘"
                , "msg": f"{model.reporting_user_name}님이 신고하신 {model.report_reason}이 삭제 처리 되었습니다."
                , "token": model.reporting_user_fcm_token
                , "image_url": model.reporting_user_profile_url
            })

        # 피 신고자
        notification = Notification(user_id=model.reported_user_id, notification_code="NOTI005"
                                    , data={"report_id": model.report_id
                , "post_id": model.post_id
                , "report_reason": model.report_reason})
        notification_list.append(notification)

        if model.reported_user_fcm_token:
            push_list.append({
                "title": "오하늘"
                , "msg": f"{model.report_reason}로 신고가 접수되어 검토 후 게시물이 삭제 처리 되었습니다."
                , "token": model.reported_user_fcm_token
                , "image_url": model.reported_user_profile_url
            })

    elif topic == KAFKA_TOPICS[4]:  # 다이어리 신고
        model = DiaryReportEvent.parse_raw(decoded_msg)

        # 신고자
        notification = Notification(user_id=model.reporting_user_id, notification_code="NOTI006"
                                    , data={"report_id": model.report_id
                , "diary_id": model.diary_id
                , "report_reason": model.report_reason})
        notification_list.append(notification)

        if model.reporting_user_fcm_token:
            push_list.append({
                "title": "오하늘"
                , "msg": f"{model.reporting_user_name}님이 신고하신 {model.report_reason}이 삭제 처리 되었습니다."
                , "token": model.reporting_user_fcm_token
                , "image_url": model.reporting_user_profile_url
            })

        # 피 신고자
        notification = Notification(user_id=model.reported_user_id, notification_code="NOTI007"
                                    , data={"report_id": model.report_id
                , "diary_id": model.diary_id
                , "report_reason": model.reported_user_fcm_token})
        notification_list.append(notification)

        if model.reported_user_fcm_token:
            push_list.append({
                "title": "오하늘"
                , "msg": f"{model.report_reason}로 신고가 접수되어 검토 후 게시물이 삭제 처리 되었습니다."
                , "token": model.reported_user_fcm_token
                , "image_url": model.reported_user_profile_url
            })

    elif topic == KAFKA_TOPICS[5]:  # 게시물 댓글
        model = PostCommentEvent.parse_raw(decoded_msg)

        notification = Notification(user_id=model.user_id, notification_code="NOTI008"
                                    , data={"comment_user_id": model.comment_user_id
                , "post_id": model.post_id
                , "comment_content": model.comment_content})
        notification_list.append(notification)

        if model.fcm_token:
            push_data = {
                "title": "오하늘"
                , "msg": f"{model.comment_user_name}님이 댓글을 남겼습니다."
                , "token": model.fcm_token
                , "image_url": model.profile_url
            }
            push_list.append(push_data)

    return notification_list, push_list


async def insert_notification(notification_list: list[Notification], db: AsyncSession):
    try:
        db.add_all(notification_list)
        await db.commit()

    except Exception as e:
        logging.error("Exception during notification insert: %s", str(e), exc_info=True)


async def send_push_notification(push_data: list[dict]):
    print(f"Push Message : {push_data}")
