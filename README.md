# Rack Provisioner Alpha v2.1

Alpha v2.1 focuses on maintainability and logical code navigation.

## Improvements

- Consistent module headers and docstrings
- Central event constants in `app/core/event_names.py`
- Documented dependency rules in `ARCHITECTURE.md`
- Complete event reference in `EVENT_CATALOG.md`
- Clearer discovery state machine
- Fixed LLDP-only workflow so it publishes `lldp.completed` instead of a full discovery result
- Removed duplicate discovery completion logic
- Preserved modular services, repositories, UI pages, SQLite, SKU revisions, and archives

## Start points

1. Read `ARCHITECTURE.md`.
2. Open `app/bootstrap.py` to see how modules connect.
3. Open `app/core/event_names.py` to see inter-module messages.
4. Open `app/discovery/service.py` for the primary workflow example.

## Run

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

The Apply button remains intentionally locked for alpha safety.
