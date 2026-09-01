# Rack Provisioner Alpha v2.2 Test Suite

This package adds a real pytest suite using:

- Fake inventory repositories for isolated service tests
- Fake event buses for event assertions
- Fake settings for inventory policy tests
- A separate temporary SQLite database for every repository test
- LLDP parser and EventBus tests

Run:

```bash
python -m pytest -q
python -m pytest --cov=app --cov-report=term-missing
```
