# TEST_STRATEGY.md

Version: Alpha v3

Status: Active

---

# Purpose

Ensure business logic functions correctly before hardware provisioning is allowed.

---

# Current Test Status

```text
58 Passed Tests
```

Additional Readiness UI tests:

```text
10 Presenter Tests Passed
```

---

# Test Layers

## Unit Tests

Uses:

```text
Fake Repositories

Fake EventBus

Fake Settings
```

---

## Integration Tests

Uses:

```text
Temporary SQLite

Real Services

Real EventBus
```

---

## UI Tests

Uses:

```text
PySide6

pytest-qt
```

---

# Event Tests

```text
Published

Received

Payload Correct
```

---

# Inventory Tests

```text
Save Rack

Update Rack

Delete Rack

Serial Match

MAC Match

Conflict Detection
```

---

# Discovery Tests

```text
Identity Parsing

Model Parsing

LLDP Parsing

Discovery Workflow
```

---

# Readiness Tests

```text
READY

BLOCKED

Warning State

SKU Failure

LLDP Failure

Profile Failure
```

---

# UI Tests

```text
READY Display

BLOCKED Display

Engineer Mode

Button Enabled

Button Disabled
```

---

# Future Tests

```text
Prompt Detection

Login Workflow

Topology Correlation

Dry Run Provisioning
```

---

# End of TEST_STRATEGY.md