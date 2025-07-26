import os
import asyncio
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .nhos_api import NiceHashAPI
from .rules_engine import RulesEngine
from .power_control import PowerController
from .notifier import Notifier
from .models import RigStatus
from dotenv import load_dotenv
import redis

load_dotenv(os.path.join('config', 'secrets.env'))

API_TOKEN = os.getenv('API_TOKEN', 'secret-token')

app = FastAPI(title="Occulis")
security = HTTPBearer()

redis_client = redis.Redis(host='localhost', port=6379, db=0)
nh_api = NiceHashAPI()
notifier = Notifier()
power = PowerController(os.path.join('config', 'relays.yaml'))
rules = RulesEngine(os.path.join('config', 'rules.yaml'), nh_api, power, notifier, redis_client)


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(nh_api.poll_loop(os.path.join('config', 'rigs.yaml'), redis_client))
    asyncio.create_task(rules.run_loop())


@app.get("/")
async def root(token: HTTPAuthorizationCredentials = Depends(verify_token)):
    rigs = {
        key.decode("utf-8"): {
            k.decode("utf-8"): v.decode("utf-8")
            for k, v in redis_client.hgetall(key).items()
        }
        for key in redis_client.keys()
    }
    return {"rigs": rigs}


@app.post("/power/reboot/{rig_name}")
async def reboot_rig(rig_name: str, token: HTTPAuthorizationCredentials = Depends(verify_token)):
    if not power.trigger_relay(rig_name):
        raise HTTPException(status_code=404, detail="Rig not found")
    return {"status": f"{rig_name} reset triggered via relay."}

