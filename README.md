# Occulis

Occulis is a Raspberry Pi based manager for NiceHash OS rigs. It polls the NiceHash API, evaluates automation rules, controls power relays, and exposes a FastAPI web interface.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure rigs and relays in `config/rigs.yaml` and `config/relays.yaml`.
3. Add NiceHash and email credentials in `config/secrets.env`.
4. Run with `uvicorn occulis_server.main:app --host 0.0.0.0 --port 8000`

## Systemd Service
An example systemd unit:

```
[Unit]
Description=Occulis Mining Manager
After=network.target

[Service]
WorkingDirectory=/path/to/Occulis
ExecStart=/usr/bin/python3 -m uvicorn occulis_server.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## Testing
Run tests with `pytest`.
Use `scripts/cycle_relay.py <rig>` to manually trigger a relay.

### API
`POST /power/reboot/{rig_name}` will pulse the GPIO relay assigned to the rig's
reset header for the configured duration. Each action is recorded in
`data/duckdb/power.duckdb`.
