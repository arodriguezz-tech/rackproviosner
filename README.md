# Rack Provisioner Alpha v3 Test Lab

A hardware-free test harness with test devices for Nokia 7215 IXS, SN4700,
SN2700, and Arista H20. It tests all currently implemented non-UI functions:
EventBus/contracts, InventoryRepository, InventoryService, identity parsing,
LLDP parsing, DiscoveryService, Readiness rules/service, and SKU revisions/archive.

Run: `python -m pytest -q`

PySide6 is not installed in this execution environment, so actual Qt widget tests
are not in this run. UI behavior should be tested separately with pytest-qt in an
environment that has PySide6 installed.
