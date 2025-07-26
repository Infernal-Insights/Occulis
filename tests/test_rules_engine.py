import os
import pytest
import asyncio
from occulis_server.rules_engine import RulesEngine
from occulis_server.power_control import PowerController
from occulis_server.notifier import Notifier

class DummyAPI:
    def __init__(self):
        self.last_id = None

    async def reboot_rig(self, rig_id):
        self.last_id = rig_id

class DummyRedis:
    def __init__(self):
        self.data = {'rig1': {b'temp': b'90'}}
    def hgetall(self, name):
        return self.data.get(name, {})

async def run_once(engine):
    task = asyncio.create_task(engine.run_loop())
    await asyncio.sleep(0.1)
    task.cancel()

@pytest.mark.asyncio
async def test_rule_trigger():
    os.environ["GPIOZERO_PIN_FACTORY"] = "mock"
    power = PowerController('config/rigs.yaml')
    notif = Notifier()
    engine = RulesEngine('config/rules.yaml', DummyAPI(), power, notif, DummyRedis())
    await run_once(engine)

class DummyHM:
    def __init__(self):
        self.last_id = None

    async def reboot_worker(self, worker_id):
        self.last_id = worker_id

@pytest.mark.asyncio
async def test_hashmancer_action(monkeypatch):
    os.environ["GPIOZERO_PIN_FACTORY"] = "mock"
    power = PowerController('config/rigs.yaml')
    notif = Notifier()
    hm = DummyHM()
    engine = RulesEngine('config/rules.yaml', DummyAPI(), power, notif, DummyRedis(), hm)
    await engine.execute_actions(['hashmancer.reboot'], 'worker1')
    assert hm.last_id == 'WORKER_ID_1'


@pytest.mark.asyncio
async def test_api_action(monkeypatch):
    os.environ["GPIOZERO_PIN_FACTORY"] = "mock"
    power = PowerController('config/relays.yaml')
    notif = Notifier()
    api = DummyAPI()
    engine = RulesEngine('config/rules.yaml', api, power, notif, DummyRedis())
    await engine.execute_actions(['api.reboot'], 'rig2')
    assert api.last_id == 'RIG_ID_2'
