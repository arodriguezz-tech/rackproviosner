# Architecture Guide

## Start here

- Application startup and dependency assembly: `app/bootstrap.py`
- Event names: `app/core/event_names.py`
- Database schemas: `app/core/database.py`
- Shared data objects: `app/domain/models.py`
- Serial transport: `app/discovery/serial.py`
- Discovery workflow: `app/discovery/service.py`
- LLDP parsing: `app/discovery/lldp.py`
- Inventory matching: `app/inventory/service.py` and `repository.py`
- SKU revisions and archives: `app/sku/service.py`
- Screens: `app/ui/pages/`

## Dependency direction

```text
UI -> Services -> Repositories -> Core database
              -> Domain models
Serial transport -> Discovery service -> Event bus -> UI/Inventory
```

Rules:

1. UI pages may call public service methods but should not execute SQL.
2. Repositories perform persistence only and should not update widgets.
3. Services implement use cases and publish outcome events.
4. Domain models contain data only.
5. Modules communicate asynchronously in intent through EventBus, even though
   Alpha v2.1 dispatch is synchronous in-process.
6. Event string literals belong in `app/core/event_names.py`.
7. Destructive switch commands remain outside the alpha.

## Adding a module

1. Add shared data to `app/domain/models.py` if needed.
2. Add persistence to a repository.
3. Add workflow logic to a service.
4. Define public outcome events in `event_names.py`.
5. Construct the service in `bootstrap.py`.
6. Subscribe from the UI or another service.
7. Add tests.
