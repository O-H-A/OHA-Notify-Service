import logging
from http.client import HTTPException

from starlette import status

from app.config.env.env import GATEWAY_URL
from app.dto.external_dto import ExternalUser, ExternalPost, ExternalDiary

logging.basicConfig(level=logging.INFO)


async def get_external_user_list(session, token, user_ids):
    if not user_ids:
        return []

    external_api_url = f"{GATEWAY_URL}/api/user/specificusers"
    headers = {"Authorization": f"Bearer {token}"}

    async with session.post(external_api_url, headers=headers, json={"userIds": list(user_ids)}) as response:
        if response.status == 201:
            api_data = await response.json()
            user_dict_list = api_data['data']
            user_list = [ExternalUser(**u) for u in user_dict_list]
            return user_list
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "사용자 정보 조회에 실패했습니다.")


async def get_external_post_list(session, token, post_ids):
    if not post_ids:
        return []

    external_api_url = f"{GATEWAY_URL}/api/posting/posts/batch-search"
    headers = {"Authorization": f"Bearer {token}"}

    async with session.post(external_api_url, headers=headers, json={"postIds": list(post_ids)}) as response:
        if response.status == 200:
            api_data = await response.json()
            post_dict_list = api_data['data']
            post_list = [ExternalPost(**p) for p in post_dict_list]
            return post_list
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "게시글 정보 조회에 실패했습니다.")


async def get_external_diary_list(session, token, diary_ids):
    if not diary_ids:
        return []

    external_api_url = f"{GATEWAY_URL}/api/diary/specificdiaries"
    headers = {"Authorization": f"Bearer {token}"}

    async with session.post(external_api_url, headers=headers, json={"diaryIds": list(diary_ids)}) as response:
        if response.status == 200:
            api_data = await response.json()
            diary_dict_list = api_data['data']
            diary_list = [ExternalDiary(**d) for d in diary_dict_list]
            return diary_list
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "다이어리 정보 조회에 실패했습니다.")
