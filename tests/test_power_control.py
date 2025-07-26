import os
import duckdb
import pytest
from occulis_server.power_control import PowerController


@pytest.mark.asyncio
async def test_trigger_relay_logs(tmp_path, monkeypatch):
    os.environ["GPIOZERO_PIN_FACTORY"] = "mock"
    db_path = tmp_path / "power.duckdb"
    pc = PowerController('config/rigs.yaml')
    # redirect database to temp path for test
    pc.db.close()
    pc.db = duckdb.connect(str(db_path))
    pc.db.execute("CREATE TABLE IF NOT EXISTS relay_log (timestamp TIMESTAMP, rig TEXT, pin INTEGER)")
    await pc.trigger_relay('rig1')
    rows = pc.db.execute("SELECT rig, pin FROM relay_log").fetchall()
    assert ('rig1', 17) in rows

