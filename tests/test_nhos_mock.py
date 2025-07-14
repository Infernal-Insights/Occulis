import asyncio
import pytest
from occulis_server.nhos_api import NiceHashAPI

class MockClient:
    async def get(self, path, headers=None, params=None):
        class Resp:
            def raise_for_status(self):
                pass
            def json(self):
                return {'temp': '90', 'hashrate': '0'}
        return Resp()

@pytest.mark.asyncio
async def test_poll_loop(monkeypatch):
    api = NiceHashAPI()
    monkeypatch.setattr(api, 'client', MockClient())
    redis = {}
    class Redis:
        def hset(self, name, mapping):
            redis[name] = mapping
    r = Redis()
    async def run_once():
        for _ in range(1):
            await api.poll_loop('config/rigs.yaml', r)
            break
    task = asyncio.create_task(run_once())
    await asyncio.sleep(0.1)
    task.cancel()
    assert 'rig1' in redis
