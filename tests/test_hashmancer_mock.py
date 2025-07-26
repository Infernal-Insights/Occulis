import asyncio
import pytest
from occulis_server.hashmancer_api import HashmancerAPI

class MockClient:
    async def get(self, path, params=None):
        class Resp:
            def raise_for_status(self):
                pass
            def json(self):
                return {'fan': '80'}
        return Resp()

@pytest.mark.asyncio
async def test_poll_loop(monkeypatch):
    api = HashmancerAPI()
    monkeypatch.setattr(api, 'client', MockClient())
    redis = {}
    class Redis:
        def hset(self, name, mapping):
            redis[name] = mapping
    r = Redis()
    task = asyncio.create_task(api.poll_loop('config/hashmancer_workers.yaml', r))
    await asyncio.sleep(0.1)
    task.cancel()
    assert 'worker1' in redis
