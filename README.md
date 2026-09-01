---
title: Rack Provisioner AI Import
project: Rack Provisioner
version: Alpha v3 Design Baseline
status: Active Development
document_type: Copilot Knowledge Package
updated: 2026-08-31
primary_users:
  - Manufacturing Technician
  - Network Engineer
supported_roles:
  - MX
  - NS1
  - NS2
tags:
  - provisioning
  - SONiC
  - inventory
  - LLDP
  - readiness
  - PySide6
  - SQLite
  - event-driven architecture
---

# Rack Provisioner — AI Import Package

> This single Markdown document consolidates the product objective, decisions, architecture, source layout, event contracts, data schema, workflows, readiness rules, user modes, testing strategy, roadmap, and current implementation state developed throughout the design conversation.

## Document Status and Accuracy Notes

- This document represents the latest **Alpha v3 design baseline** discussed in the project conversation.
- It consolidates code and test artifacts that were produced in separate prototype packages.
- It is not a claim that every described feature is already integrated into one executable application.
- Actual switch configuration application remains intentionally disabled in the Alpha safety model.
- The latest executed non-UI test lab reported **58 passing tests**.
- The later Readiness UI starter reported **10 headless presenter tests passing and one Qt UI test module skipped** because PySide6 was unavailable in that execution environment.

---

# 1. Project Objective

## Primary Objective

Create a safe, user-friendly rack-switch provisioning application that automatically identifies and validates the MX, NS1, and NS2 devices for a rack, confirms that inventory, hardware, configuration profiles, and expected network connections agree, and permits provisioning only after a centralized Readiness Engine returns **READY**.

## Objective Statement

> Reduce manufacturing configuration errors and technician decision-making by replacing manual script selection and command-line interaction with a guided workflow based on Rack Serial Number, local inventory, switch identity discovery, SKU/profile selection, LLDP connection validation, revision-controlled configuration, and an explicit READY or BLOCKED safety decision.

## User Outcome

A technician should be able to:

```text
Select Rack Position
        ↓
Enter or scan Rack Serial Number
        ↓
Load local rack inventory
        ↓
Connect to MX / NS1 / NS2 over serial
        ↓
Automatically identify model, serial, and MAC
        ↓
Verify inventory and assigned roles
        ↓
Validate expected LLDP neighbors and ports
        ↓
Load the correct SKU and profiles
        ↓
Evaluate readiness
        ↓
Review friendly READY or BLOCKED status
        ↓
Generate a dry run
        ↓
Provision only when explicitly allowed
```

The technician must not need to:

- Select raw shell scripts manually.
- Assign MX, NS1, or NS2 roles by console-cable order.
- Read raw SONiC commands.
- Interpret internal event names.
- Understand database structure.
- Ignore or bypass identity conflicts.

## Business Goals

1. Prevent the wrong configuration from being applied to a switch.
2. Reduce rack rework caused by incorrect role assignment, model selection, or cabling.
3. Improve provisioning consistency and repeatability.
4. Preserve configuration and SKU history through automatic revisions and archives.
5. Build an auditable local inventory keyed by Rack Serial Number.
6. Provide technician-friendly language while retaining engineer diagnostics.
7. Collect structured results for future reporting and process improvement.

## Non-Goals for Current Alpha

- Production configuration push.
- Factory reset automation.
- Firmware deployment.
- Blade inventory or blade topology management.
- Live company inventory-site scraping.
- Inventory database writeback.
- BSL automation.
- Automatic external API integration.

---

# 2. Product Decisions Captured from the Design Discussion

## Scope Decisions

- V1/Alpha focuses on MX, NS1, and NS2 only.
- Blade tracking and `RACK_MGMT_MAP` population management are deferred.
- Rack Position is operational job data, not imported inventory data.
- Allowed Rack Positions are currently `RK1617` through `RK1632`.
- Rack Serial Number is the primary inventory lookup key.
- Inventory can be built manually in a dedicated Inventory Manager page.
- CSV and JSON inventory import remain feature-flagged future capabilities.
- Website capture, web scraping, and embedded company-site automation are deferred.

## Safety Decisions

- Inventory role identity may be matched by serial number or MAC address.
- A serial/MAC role conflict is always a blocking condition.
- Readiness is the only authority that enables provisioning.
- Raw command execution remains hidden from end users.
- Engineer Mode exposes diagnostic reasoning, not unrestricted dangerous controls.
- The Alpha Apply button remains locked.

## Revision Decisions

- Revision format is `Major.Minor`, for example `1.0`, `1.1`, `2.0`.
- Model changes force a major revision.
- Script/configuration changes normally create a minor revision.
- Superseded revisions are archived, never deleted.
- Revision metadata belongs in SQLite and archive metadata, not only filenames.

---

# 3. High-Level Architecture

## Layered Architecture

```text
Presentation Layer
    PySide6 pages and widgets
            ↓
Application Services
    Inventory, Discovery, Readiness, SKU
            ↓
Repositories
    SQLite persistence and queries
            ↓
Storage
    inventory.db, provisioning.db, archives
```

Shared infrastructure:

```text
EventBus
SettingsService
FeatureFlags
Domain Models
Friendly Message Catalog
```

## Dependency Rules

Allowed:

```text
UI → Services
Services → Repositories
Services → Domain Models
Repositories → SQLite
Services → EventBus
UI → EventBus subscriptions
```

Not allowed:

```text
UI → raw SQL
UI → direct readiness calculations
Inventory → UI widgets
Discovery → SKU editor widgets
Repository → EventBus
Domain Models → Qt or SQLite
```

## Dependency Injection

The application bootstrap creates one shared instance of each dependency and injects it into consumers:

```python
bus = EventBus()
settings = SettingsService()
inventory_repository = InventoryRepository(inventory_database_path)
inventory_service = InventoryService(
    inventory_repository,
    bus,
    settings,
)
readiness_service = ReadinessService(
    bus,
    readiness_rules,
)
```

Pages receive those instances rather than constructing their own databases, services, or event buses.

---

# 4. Repository and Code Structure

```text
rack-provisioner/
├── app/
│   ├── bootstrap.py
│   ├── core/
│   │   ├── database.py
│   │   ├── event_names.py
│   │   ├── events.py
│   │   ├── feature_flags.py
│   │   ├── paths.py
│   │   └── settings.py
│   ├── domain/
│   │   ├── constants.py
│   │   ├── enums.py
│   │   └── models.py
│   ├── inventory/
│   │   ├── exceptions.py
│   │   ├── models.py
│   │   ├── repository.py
│   │   ├── service.py
│   │   └── validators.py
│   ├── discovery/
│   │   ├── lldp.py
│   │   ├── login_service.py          # planned
│   │   ├── parser.py
│   │   ├── prompt_detector.py        # next phase
│   │   ├── serial_session.py
│   │   └── service.py
│   ├── readiness/
│   │   ├── messages.py
│   │   ├── models.py
│   │   ├── presenter.py
│   │   ├── rules.py
│   │   └── service.py
│   ├── sku/
│   │   ├── archive.py
│   │   ├── models.py
│   │   ├── repository.py
│   │   └── service.py
│   ├── topology/                     # planned
│   │   ├── correlator.py
│   │   ├── models.py
│   │   └── validation.py
│   ├── provisioning/                 # planned
│   │   ├── dry_run.py
│   │   ├── models.py
│   │   └── renderer.py
│   ├── reporting/                    # planned
│   │   ├── exports.py
│   │   ├── repository.py
│   │   └── service.py
│   └── ui/
│       ├── main_window.py
│       ├── highlighter.py
│       ├── pages/
│       │   ├── inventory_manager.py
│       │   ├── inventory_mapping.py
│       │   ├── multi_switch.py
│       │   ├── settings.py
│       │   ├── single_switch.py
│       │   └── sku_manager.py
│       └── widgets/
│           ├── event_monitor.py
│           ├── readiness_panel.py
│           └── status_banner.py
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── ui/
│   ├── conftest.py
│   └── fakes.py
├── docs/
├── data/
│   ├── inventory.db
│   └── provisioning.db
├── archive/
├── reports/
├── pyproject.toml
├── settings.ini
└── README.md
```

---

# 5. Domain Models

## DeviceIdentity

```python
@dataclass
class DeviceIdentity:
    serial: str = ""
    mac: str = ""
    model: str = ""
    role: str | None = None
```

## LldpNeighbor

```python
@dataclass
class LldpNeighbor:
    local_port: str
    neighbor_mac: str = ""
    neighbor_name: str = ""
    neighbor_ip: str = ""
    neighbor_port: str = ""
```

## DiscoveryResult

```python
@dataclass
class DiscoveryResult:
    identity: DeviceIdentity
    neighbors: list[LldpNeighbor]
    raw_outputs: dict[str, str]
```

## RuleResult

```python
@dataclass
class RuleResult:
    name: str
    status: str
    code: str = ""
    message: str = ""
```

## ReadinessResult

```python
@dataclass
class ReadinessResult:
    ready: bool
    status: str
    checks: list[RuleResult]
    blockers: list[str]
    warnings: list[str]
```

---

# 6. Event Catalog and Payload Contracts

## Active Events

### `serial.connected`

```python
{
    "ok": bool,
    "port": str,
    "baud": int,
}
```

### `serial.command.finished`

```python
{
    "name": str,
    "output": str,
}
```

### `discovery.completed`

```python
{
    "result": DiscoveryResult,
}
```

### `lldp.completed`

```python
{
    "neighbors": list[LldpNeighbor],
    "raw_output": str,
}
```

### `inventory.saved`

```python
{
    "rack_serial": str,
}
```

### `inventory.verified`

```python
{
    "state": str,
    "role": str | None,
    "reason": str,
    "rack_serial": str,
}
```

Valid inventory states:

- `VERIFIED`
- `UNKNOWN`
- `CONFLICT`
- `DISABLED`

### `sku.revision.saved`

```python
{
    "sku": str,
    "version": str,
    "revision_type": str,
    "changes": list[str],
}
```

### `settings.changed`

```python
{}
```

### `readiness.evaluated`

```python
{
    "result": ReadinessResult,
}
```

## Planned Events

- `prompt.detected`
- `login.completed`
- `rack.discovery.completed`
- `topology.correlated`
- `dry_run.completed`
- `report.generated`

## Event Testing Contract

Every active event must be tested for:

1. **Published** — the canonical event name is emitted.
2. **Received** — named subscribers receive exactly one event.
3. **Payload Correct** — values and required fields are preserved.

---

# 7. Database Schema

## `inventory.db`

### `racks`

```sql
CREATE TABLE racks (
    rack_serial TEXT PRIMARY KEY,
    rack_sku TEXT NOT NULL,
    rack_bom TEXT,
    rack_asset_tag TEXT,
    created_at TEXT NOT NULL,
    modified_at TEXT NOT NULL
);
```

### `devices`

```sql
CREATE TABLE devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rack_serial TEXT NOT NULL,
    role TEXT NOT NULL,
    model TEXT,
    serial_number TEXT,
    normalized_serial TEXT,
    mac_address TEXT,
    normalized_mac TEXT,
    notes TEXT,
    UNIQUE (rack_serial, role),
    FOREIGN KEY (rack_serial)
        REFERENCES racks(rack_serial)
        ON DELETE CASCADE
);
```

Indexes:

```sql
CREATE INDEX idx_device_serial
ON devices(normalized_serial);

CREATE INDEX idx_device_mac
ON devices(normalized_mac);
```

## `provisioning.db`

Planned/current scaffold tables:

- `sku`
- `sku_content`
- `sku_revision`
- `jobs`
- `validation_results` — planned
- `inventory_events` — planned

## Data Ownership

- Inventory identity belongs only in `inventory.db`.
- Rack Position belongs to a provisioning job, not the permanent rack identity.
- SKU content and revisions belong in the SKU repository/database.
- Raw discovery information belongs to job/report history, not inventory identity.

---

# 8. Inventory Manager

## Purpose

Create, edit, search, and delete local rack inventory without relying on an unknown external export format.

## Rack Fields

- Rack Serial Number — required and primary key.
- Rack SKU — required.
- Rack BOM — optional.
- Rack Asset Tag — optional.

## Device Roles

Every saved rack requires:

- MX
- NS1
- NS2

Each device contains:

- Model
- Serial Number
- MAC Address

At least one device identity value, serial or MAC, is required.

## Validation

- Required Rack Serial.
- Required Rack SKU.
- Required roles.
- No duplicate roles.
- Model required per role.
- Valid normalized MAC when provided.
- No duplicate serial numbers.
- No duplicate MAC addresses.
- Serial and MAC matching different roles returns `CONFLICT`.

## Future Import

Settings retain future flags for:

- CSV import.
- JSON import.

Both importers must populate the same repository used by manual entry.

---

# 9. Discovery and LLDP

## Current Read-Only Discovery

The internal implementation may collect:

- Platform/version information.
- EEPROM identity information.
- LLDP neighbors.

Technicians do not see the raw commands.

## User-Friendly Progress

```text
Connecting to switch
Identifying hardware
Verifying inventory
Checking network connections
Loading configuration
Evaluating readiness
```

## LLDP Fields Parsed

- Local port.
- Neighbor chassis MAC.
- Neighbor system name.
- Neighbor management IP.
- Neighbor remote port.

## LLDP Role

LLDP is corroborating topology evidence, not the sole source of role identity.

Identity priority:

```text
Inventory serial/MAC
        +
Direct discovery
        +
LLDP topology evidence
```

A topology mismatch must not silently reassign a role.

---

# 10. SKU and Revision System

## SKU Relationship

```text
Rack Serial
    ↓
Rack SKU
    ↓
Role
    ↓
Profile
    ↓
Configuration Variables
    ↓
Generated Configuration
```

## Revision Format

```text
Major.Minor
```

Examples:

```text
1.0
1.1
1.2
2.0
2.1
```

## Major Triggers

- Device model change.
- Vendor change.
- Role addition/removal.
- Hardware structure change.
- Future topology definition change.

## Minor Triggers

- Configuration text change.
- Hostname or management template change.
- Port-speed configuration change.
- VLAN change.
- Validation-rule change.

## Archive

Superseded revisions are stored as `.tar.gz` packages containing metadata and checksums. Revision metadata is authoritative in SQLite; filenames are only a convenience.

---

# 11. Readiness Engine

## Purpose

The Readiness Engine is the single decision authority that determines whether provisioning may proceed.

## Rule Statuses

- `PASS`
- `WARNING`
- `FAIL`

## Final Statuses

- `READY`
- `BLOCKED`

## Current Rules

### Inventory Rule

- `VERIFIED` → PASS
- `DISABLED` → WARNING when policy permits
- `UNKNOWN` → FAIL
- `CONFLICT` → FAIL

Code: `INV-001`

### Discovery Rule

Requires serial identity and model identity.

Code: `DISC-001`

### SKU Model Rule

Discovered model must match the expected model assigned to the role/SKU.

Code: `SKU-001`

### LLDP Rule

Minimum required neighbors must be visible. Full fixed-port topology correlation is planned.

Code: `LLDP-001`

### Profile Rule

A configuration profile must be available for the SKU role.

Code: `PROF-001`

## Provisioning Gate

```python
start_button.setEnabled(readiness_result.ready)
```

The UI must never reproduce readiness rules independently.

---

# 12. Technician and Engineer Modes

## Technician Mode

Displays:

- Inventory information verified.
- Switch identified.
- Hardware matches rack configuration.
- Required network connections detected.
- Configuration is available.
- Ready to provision.
- Provisioning blocked with corrective guidance.

Never displays:

- Raw commands.
- Raw CLI output.
- Event names.
- Internal error codes.
- SQL.
- Debug payloads.

## Engineer Mode

Adds:

- Rule names and statuses.
- Block codes.
- Technical explanations.
- LLDP neighbor details.
- Inventory match reasoning.
- Event monitor.
- Revision history.

Engineer Mode is a visibility feature, not an automatic bypass authorization.

## Friendly Messages

```text
DISC-001
The switch could not be identified completely.

INV-001
Inventory information could not be verified.

SKU-001
The detected hardware does not match this rack configuration.

LLDP-001
Required network connections were not detected.

PROF-001
The required switch configuration is unavailable.
```

---

# 13. UI Navigation

## Technician Navigation

```text
Single Switch
Multi Switch
Inventory Manager
Inventory Mapping
SKU Manager
Readiness
Settings
```

## Engineer-Only Visibility

```text
Readiness Details
Event Monitor
Revision History
Topology View         # future
```

## Rack Position

Rack Position is selected from:

```text
RK1617 through RK1632
```

It belongs to the provisioning job record.

---

# 14. Testing Strategy and Detailed Test Areas

## Test Layers

### Unit Tests

Use:

- Fake repositories.
- Fake event buses.
- Fake settings.
- Fake serial transport.

### Integration Tests

Use:

- Real services.
- Real EventBus.
- Temporary SQLite databases.

### UI Tests

Use:

- PySide6.
- pytest-qt.
- Offscreen Qt platform in CI.

## Validated Non-UI Areas

The latest hardware-free test lab reported 58 passing tests covering:

- Event Bus.
- Event contracts.
- Inventory Repository.
- Inventory Service.
- Identity parser.
- LLDP parser.
- Discovery Service.
- Readiness rules and service.
- SKU revision and archive logic.
- Representative test devices.

## Readiness UI Test Status

The Readiness UI starter reported:

- 10 presenter tests passed.
- One UI test module skipped because PySide6 was unavailable in that environment.
- Python syntax compilation passed.

## Required Event Tests

For each active event:

- Published.
- Received.
- Payload Correct.
- Missing required payload rejected where contracts apply.

## Inventory Repository Cases

- Save rack and three devices.
- Retrieve rack.
- Upsert rack.
- Upsert device role.
- Delete rack and cascade devices.
- Serial normalization.
- MAC normalization.
- Serial-only verification.
- MAC-only verification.
- Serial+MAC verification.
- Conflict detection.
- Cross-rack isolation.
- Unknown identity.

## Inventory Service Cases

- Required Rack Serial.
- Required Rack SKU.
- Missing role.
- Duplicate role.
- Missing model.
- Missing identity.
- Invalid MAC.
- Duplicate serial.
- Duplicate MAC.
- Inventory enabled verification.
- Inventory disabled behavior.
- Event publication.

## Discovery and LLDP Cases

- Serial parsing.
- MAC parsing.
- Model parsing.
- Missing values.
- Full discovery workflow.
- LLDP-only workflow.
- Empty LLDP output.
- Multiple LLDP neighbors.
- Port and MAC extraction.

## Readiness Cases

- Fully READY.
- Inventory unknown.
- Inventory conflict.
- Inventory disabled warning.
- Discovery incomplete.
- Model mismatch.
- Missing LLDP neighbor.
- Missing profile.
- `readiness.evaluated` publication.

## Readiness UI Cases

- Safe initial state.
- Start button initially disabled.
- READY enables action.
- BLOCKED disables action.
- Friendly blocker message appears.
- Technician hides codes/details.
- Engineer Mode shows codes/details.
- Unknown code receives generic safe message.

---

# 15. Roadmap

## Alpha v3 Phase 1 — Readiness UI

- Integrate Readiness Panel.
- Subscribe to `readiness.evaluated`.
- Add friendly text presenter.
- Add Engineer Mode details.
- Gate provisioning button.
- Run pytest-qt in a Qt-enabled environment.

## Phase 2 — Prompt Detection

- Detect login, password, shell, ONIE, GRUB, and unknown states.
- Publish `prompt.detected`.
- Add Prompt Readiness Rule.
- Keep raw prompts hidden in Technician Mode.

## Phase 3 — Login Workflow

- Add login state machine.
- Handle timeout and invalid authentication.
- Publish `login.completed`.
- Keep credentials outside logs and SQLite.

## Phase 4 — LLDP Topology Correlation

- Define expected fixed local and remote ports per SKU role.
- Correlate neighbor MACs against inventory.
- Detect wrong neighbor, wrong port, missing neighbor, and cross-rack neighbor.
- Publish `topology.correlated`.

## Phase 5 — Multi-Switch Coordinator

- Coordinate independent MX, NS1, and NS2 workers.
- Aggregate device readiness.
- Publish `rack.discovery.completed`.
- Rack READY only when required device readiness passes.

## Phase 6 — Dry-Run Provisioning

- Render profiles and variables.
- Validate unresolved variables.
- Generate user-friendly dry-run summary.
- Do not send configuration.
- Publish `dry_run.completed`.

## Phase 7 — Reporting

- Store jobs, durations, results, blocker codes, and validation outcomes.
- Generate daily/weekly summaries.
- Publish `report.generated`.

---

# 16. Changelog

## Alpha v1

- Initial concept.
- Single-switch and multi-switch workflow direction.
- SKU-based script selection.

## Alpha v2

- Modular architecture.
- Event Bus.
- Dependency injection.
- Inventory repository and service.
- LLDP parsing.
- SKU revision and archive design.
- Automated tests.

## Alpha v2.3

- Formal event payload contracts.
- Published/Received/Payload Correct test matrix.

## Alpha v3 Design Baseline

- Readiness Engine.
- Readiness rules and block codes.
- Technician-friendly message layer.
- Engineer Mode visibility.
- Readiness UI starter and tests.
- Prompt Detection selected as the next feature after UI integration.

---

# 17. Current State Summary

## Implemented or Prototyped

- Modular code structure.
- Event-driven communication.
- Dependency injection pattern.
- Local inventory schema and CRUD logic.
- Serial/MAC identity matching.
- LLDP parser.
- SKU revisions and archives.
- Readiness rules/service.
- Friendly Readiness presenter.
- Readiness Panel starter.
- Automated non-UI tests.
- Conditional pytest-qt tests.

## Not Yet Production-Integrated

- Full latest app assembled from all separate prototype packages.
- Prompt Detection.
- Login automation.
- Multi-switch coordination.
- Full topology correlation.
- Dry-run renderer.
- Reporting implementation.
- Real provisioning push.

## Next Objective

Complete Readiness UI integration into the main application, validate the widget tests in a PySide6/pytest-qt environment, then implement Prompt Detection as an additional readiness input.

---

# 18. AI Guidance for Future Work

When modifying this project:

1. Preserve Rack Serial Number as the inventory primary key.
2. Keep Rack Position as job data.
3. Do not display raw commands to technicians.
4. Do not let UI pages execute SQL.
5. Do not duplicate readiness calculations in the UI.
6. Add new event names centrally.
7. Document and test every event payload.
8. Add a rule instead of hard-coding a new provisioning gate.
9. Treat serial/MAC conflicts as blockers.
10. Keep actual configuration application disabled until prompt, login, topology, dry-run, and hardware-lab tests are complete.
