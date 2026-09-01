"""Canonical event names.

Use constants instead of repeating string literals across modules. This prevents
typographical event bugs and makes event discovery easy for maintainers.
"""

# Serial transport events
SERIAL_CONNECTED = "serial.connected"
SERIAL_DISCONNECTED = "serial.disconnected"
SERIAL_BLOCKED = "serial.blocked"
SERIAL_ERROR = "serial.error"
SERIAL_COMMAND_STARTED = "serial.command.started"
SERIAL_COMMAND_FINISHED = "serial.command.finished"
CONSOLE_RECEIVED = "console.received"

# Discovery workflow events
DISCOVERY_STARTED = "discovery.started"
DISCOVERY_COMMAND_COMPLETED = "discovery.command.completed"
DISCOVERY_COMPLETED = "discovery.completed"
LLDP_COMPLETED = "lldp.completed"

# Inventory events
INVENTORY_SAVED = "inventory.saved"
INVENTORY_VERIFIED = "inventory.verified"

# SKU and application events
SKU_REVISION_SAVED = "sku.revision.saved"
SETTINGS_CHANGED = "settings.changed"
