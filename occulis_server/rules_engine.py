import asyncio
import time
import yaml
from typing import Dict, Any


class RulesEngine:
    def __init__(self, rules_path: str, api, power, notifier, redis_client, hashmancer_api=None):
        self.rules_path = rules_path
        self.api = api
        self.hm_api = hashmancer_api
        self.power = power
        self.notifier = notifier
        self.redis = redis_client
        with open(rules_path, 'r') as f:
            self.rules = yaml.safe_load(f) or []
        # load rig and worker mappings for reboot actions
        with open('config/rigs.yaml', 'r') as f:
            self.rig_map = yaml.safe_load(f) or {}
        with open('config/hashmancer_workers.yaml', 'r') as f:
            self.worker_map = yaml.safe_load(f) or {}
        self.state = {}

    def _evaluate_condition(self, rig_data: Dict[str, Any], condition: str) -> bool:
        try:
            return eval(condition, {}, rig_data)
        except Exception:
            return False

    async def run_loop(self):
        while True:
            for rule in self.rules:
                rig_name = rule.get('rig')
                rig_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in self.redis.hgetall(rig_name).items()}
                if not rig_data:
                    continue
                cond = self._evaluate_condition(rig_data, rule['condition'])
                if cond:
                    key = f"{rig_name}:{rule['condition']}"
                    first = self.state.get(key)
                    now = time.time()
                    if not first:
                        self.state[key] = now
                    elif now - first >= rule.get('duration', 0):
                        await self.execute_actions(rule['actions'], rig_name)
                        self.state.pop(key, None)
                else:
                    self.state.pop(f"{rig_name}:{rule['condition']}", None)
            await asyncio.sleep(30)

    async def execute_actions(self, actions, rig_name):
        for act in actions:
            if act == 'api.reboot':
                rig_id = self.rig_map.get(rig_name, rig_name)
                await self.api.reboot_rig(rig_id)
            elif act == 'hashmancer.reboot' and self.hm_api:
                worker_id = self.worker_map.get(rig_name, rig_name)
                await self.hm_api.reboot_worker(worker_id)
            elif act == 'power.gpio_cycle':
                self.power.cycle_relay(rig_name)
            elif act == 'notify.email':
                self.notifier.send_email(f"Rule triggered for {rig_name}")
