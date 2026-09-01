# Rack Provisioner Alpha v2

Alpha v2 reorganizes the prototype into modules with an in-process event bus.

## Modules
- `app/core`: paths, settings, SQLite initialization, event bus
- `app/domain`: shared dataclasses
- `app/discovery`: serial transport, identity parsing, LLDP parsing, discovery orchestration
- `app/inventory`: inventory repository and identity verification service
- `app/sku`: SKU persistence, revision classification, checksums, tar.gz archive service
- `app/ui`: window, pages, and syntax highlighting

## Event flow
`SerialSession -> DiscoveryService -> EventBus -> UI / InventoryService`

Key events include `serial.connected`, `serial.command.started`, `serial.command.finished`, `discovery.started`, `discovery.command.completed`, `discovery.completed`, `inventory.verified`, `sku.revision.saved`, and `settings.changed`.

## Safety
Apply remains locked. Only read-only discovery commands are sent in the alpha.

## Run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Tests
```bash
python -m pytest
```
