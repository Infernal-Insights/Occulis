# Occulis

Occulis is a Raspberry Pi based manager for NiceHash OS rigs. It polls the NiceHash API, evaluates automation rules, controls power relays, and exposes a FastAPI web interface.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure rigs in `config/rigs.yaml`.
   Example:
   ```yaml
   rig1:
     type: nicehash
     id: RIG_ID_1
     pin: 17
   worker1:
     type: hashmancer
     id: WORKER_ID_1
     pin: 2
   ```
3. Add NiceHash, Hashmancer, and email credentials in `config/secrets.env`.
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

## Display Status Screen
A simple Tkinter interface can show current rig statistics on a Raspberry Pi 7" display. It is independent of the FastAPI dashboard and won't interfere with other monitoring tools. Launch it with:

```bash
python scripts/display_status.py [--host localhost] [--port 6379] [--interval 5000]
```

The script polls Redis for rig data and updates the screen every few seconds. Redis connection parameters can also be provided via the environment variables `OCCULIS_REDIS_HOST` and `OCCULIS_REDIS_PORT`.

### Environment Variables
* `HM_API_URL` - base URL for Hashmancer's FastAPI (default `http://localhost:8001`).
* `HM_API_TOKEN` - optional bearer token for authenticated requests.
* `API_TOKEN` - NiceHash API bearer token.
* `NH_ORG_ID` - NiceHash organization ID.
* `NH_API_KEY` - NiceHash API key.
* `NH_API_SECRET` - NiceHash API secret.

These credentials should be stored in `config/secrets.env`.
