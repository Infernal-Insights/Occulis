import os
import asyncio
import httpx
import yaml
from dotenv import load_dotenv

load_dotenv(os.path.join('config', 'secrets.env'))

API_URL = os.getenv('HM_API_URL', 'http://localhost:8001')
API_TOKEN = os.getenv('HM_API_TOKEN')


class HashmancerAPI:
    def __init__(self):
        headers = {}
        if API_TOKEN:
            headers['Authorization'] = f'Bearer {API_TOKEN}'
        self.client = httpx.AsyncClient(base_url=API_URL, headers=headers)

    async def get(self, path: str, params=None):
        resp = await self.client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    async def post(self, path: str, json=None):
        resp = await self.client.post(path, json=json)
        resp.raise_for_status()
        return resp.json()

    async def poll_loop(self, workers_config: str, redis_client):
        with open(workers_config, 'r') as f:
            workers = yaml.safe_load(f) or {}
        while True:
            for name, worker_id in workers.items():
                try:
                    stats = await self.get(f'/workers/{worker_id}/stats')
                    redis_client.hset(name, mapping=stats)
                except Exception as e:
                    redis_client.hset(name, mapping={'error': str(e)})
            await asyncio.sleep(30)

    async def reboot_worker(self, worker_id: str):
        await self.post(f'/workers/{worker_id}/reboot')
