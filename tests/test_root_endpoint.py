import os
import importlib
import sys
import pytest
from fastapi.security import HTTPAuthorizationCredentials


@pytest.mark.asyncio
async def test_root_decodes(monkeypatch):
    os.environ["GPIOZERO_PIN_FACTORY"] = "mock"

    # Stub PowerController before importing main module to avoid GPIO usage
    class DummyPC:
        def __init__(self, *args, **kwargs):
            pass
    pc_module = importlib.import_module('occulis_server.power_control')
    monkeypatch.setattr(pc_module, 'PowerController', DummyPC)

    main_module = importlib.import_module('occulis_server.main')

    class DummyRedis:
        def __init__(self):
            self.store = {b'rig1': {b'temp': b'75', b'hashrate': b'100'}}
        def keys(self):
            return list(self.store.keys())
        def hgetall(self, key):
            return self.store[key]
    dummy = DummyRedis()
    monkeypatch.setattr(main_module, 'redis_client', dummy)

    token = HTTPAuthorizationCredentials(scheme="Bearer", credentials=main_module.API_TOKEN)
    result = await main_module.root(token)
    assert result == {'rigs': {'rig1': {'temp': '75', 'hashrate': '100'}}}
