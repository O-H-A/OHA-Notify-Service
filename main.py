import uvicorn
from fastapi import FastAPI, APIRouter
import py_eureka_client.eureka_client as eureka_client
from config.env import HOST, PORT, EUREKA_SERVER, EUREKA_APP_NAME, RELOAD

app = FastAPI(docs_url='/api/notify/docs', openapi_url='/api/notify/openapi.json')

router = APIRouter()

if __name__ == "__main__":
    eureka_client.init(eureka_server=EUREKA_SERVER,
                       app_name=EUREKA_APP_NAME,
                       instance_host=HOST,
                       instance_port=int(PORT))

    uvicorn.run("main:app", host='0.0.0.0', port=int(PORT), reload=RELOAD, )
