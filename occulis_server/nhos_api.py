import os
import asyncio
import httpx
import yaml
from typing import Dict

from dotenv import load_dotenv

load_dotenv(os.path.join('config', 'secrets.env'))

API_URL = 'https://api2.nicehash.com'
ORGANIZATION_ID = os.getenv('NH_ORG_ID')
API_KEY = os.getenv('NH_API_KEY')
API_SECRET = os.getenv('NH_API_SECRET')


class NiceHashAPI:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=API_URL)

    async def get(self, path: str, params: Dict[str, str] = None):
        headers = {
            'X-Organization-Id': ORGANIZATION_ID or '',
            'X-Api-Key': API_KEY or ''
        }
        resp = await self.client.get(path, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()

    async def poll_loop(self, rigs_config: str, redis_client):
        with open(rigs_config, 'r') as f:
            rigs = yaml.safe_load(f)
        while True:
            for name, rig_id in rigs.items():
                try:
                    stats = await self.get(f'/main/api/v2/mining/rig/stats/{rig_id}')
                    redis_client.hset(name, mapping=stats)
                except Exception as e:
                    redis_client.hset(name, mapping={'error': str(e)})
            await asyncio.sleep(30)

    async def reboot_rig(self, rig_id: str):
        path = f'/main/api/v2/mining/rigs/status2'  # hypothetical
        await self.get(path, params={'rigId': rig_id, 'action': 'REBOOT'})
