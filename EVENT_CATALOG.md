# Event Catalog

| Event | Publisher | Typical subscribers | Payload |
|---|---|---|---|
| `serial.connected` | SerialSession | SingleSwitchPage | `ok`, `port`, `baud` |
| `serial.disconnected` | SerialSession | SingleSwitchPage | none |
| `serial.command.started` | SerialSession | UI/logger | `name`, `command` |
| `serial.command.finished` | SerialSession | DiscoveryService | `name`, `output` |
| `console.received` | DiscoveryService | Console pane/logger | `text` |
| `discovery.started` | DiscoveryService | UI/job tracking | none |
| `discovery.command.completed` | DiscoveryService | Progress UI | `command` |
| `discovery.completed` | DiscoveryService | UI/validation | `result` |
| `lldp.completed` | DiscoveryService | UI/topology validator | `neighbors`, `raw_output` |
| `inventory.saved` | InventoryService | UI/audit | `rack_serial` |
| `inventory.verified` | InventoryService | UI/readiness | `state`, `role`, `reason`, `rack_serial` |
| `sku.revision.saved` | SkuService | UI/history view | `sku`, `version`, `revision_type`, `changes` |
| `settings.changed` | SettingsPage | MainWindow/services | none |
