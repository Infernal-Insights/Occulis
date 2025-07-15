import yaml
import time
import duckdb
from datetime import datetime
try:
    from gpiozero import OutputDevice
except ImportError:  # for development without GPIO
    class OutputDevice:
        def __init__(self, pin, active_high=False, initial_value=False):
            self.pin = pin
        def on(self):
            print(f"Relay {self.pin} ON")
        def off(self):
            print(f"Relay {self.pin} OFF")

def load_relays(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f) or {}


class PowerController:
    def __init__(self, relays_path: str):
        self.relays_config = load_relays(relays_path)
        self.relays = {
            name: OutputDevice(cfg['pin'], active_high=False, initial_value=True)
            for name, cfg in self.relays_config.items()
        }
        self.db = duckdb.connect('data/duckdb/power.duckdb')
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS relay_log (timestamp TIMESTAMP, rig TEXT, pin INTEGER)"
        )

    def cycle_relay(self, rig_name: str) -> bool:
        return self.trigger_relay(rig_name)

    def trigger_relay(self, rig_name: str) -> bool:
        cfg = self.relays_config.get(rig_name)
        relay = self.relays.get(rig_name)
        if not cfg or not relay:
            return False
        relay.on()
        time.sleep(cfg.get('pulse_seconds', 1))
        relay.off()
        self.db.execute(
            "INSERT INTO relay_log VALUES (?, ?, ?)",
            [datetime.utcnow(), rig_name, cfg['pin']],
        )
        return True
