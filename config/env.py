import os

PROFILE = os.environ.get("PROFILE", 'local')
DB_URL = os.environ.get("DB_URL")

DB_SCHEMA = None
HOST = None
PORT = None
EUREKA_SERVER = None
EUREKA_APP_NAME = None
RELOAD = None

if PROFILE == 'local':
    DB_SCHEMA = 'dev'
    HOST = '127.0.0.1'
    PORT = os.environ.get("PORT")
    EUREKA_SERVER = 'http://localhost:8761'
    EUREKA_APP_NAME = 'notify-service-dev'
    RELOAD = True

elif PROFILE == 'dev':
    DB_SCHEMA = 'dev'
    HOST = os.environ.get("HOST")
    PORT = os.environ.get("PORT")
    EUREKA_SERVER = os.environ.get("EUREKA_SERVER")
    EUREKA_APP_NAME = 'notify-service-dev'
    RELOAD = False

elif PROFILE == 'pd':
    DB_SCHEMA = 'public'
    HOST = os.environ.get("HOST")
    PORT = os.environ.get("PORT")
    EUREKA_SERVER = os.environ.get("EUREKA_SERVER")
    EUREKA_APP_NAME = 'notify-service'
    RELOAD = False


