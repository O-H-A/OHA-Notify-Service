import asyncio

from app.config.env.env import KAFKA_HOST, KAFKA_PORT, PROFILE, KAFKA_OFFSET

KAFKA_TOPICS = [
    f'post-like-user-{PROFILE}'
    , f'diary-like-user-{PROFILE}'
    , f'weather-reg-user-{PROFILE}'
    , f'post-report-user-{PROFILE}'
    , f'diary-report-user-{PROFILE}'
    , f'post-comment-user-{PROFILE}'
]
KAFKA_BOOTSTRAP_SERVERS = [f'{KAFKA_HOST}:{KAFKA_PORT}']
KAFKA_CONSUMER_GROUP = "notify-group"
loop = asyncio.get_event_loop()
KAFKA_AUTO_OFFSET_RESET = "latest"
