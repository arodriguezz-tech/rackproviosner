# READINESS_ENGINE.md

Version: Alpha v3

Status: Active

---

# Purpose

Determine whether provisioning is allowed.

Readiness is the only authority that enables provisioning.

---

# Status Types

```text
PASS

WARNING

FAIL
```

---

# Final Results

```text
READY

BLOCKED
```

---

# Rules

## Inventory Rule

PASS:

```text
VERIFIED
```

WARNING:

```text
DISABLED
```

FAIL:

```text
UNKNOWN

CONFLICT
```

Code:

```text
INV-001
```

---

## Discovery Rule

Checks:

```text
Serial Present

Model Present
```

Code:

```text
DISC-001
```

---

## SKU Rule

Checks:

```text
Expected Model

Discovered Model
```

Code:

```text
SKU-001
```

---

## LLDP Rule

Checks:

```text
Required Neighbors
```

Code:

```text
LLDP-001
```

---

## Profile Rule

Checks:

```text
Configuration Exists
```

Code:

```text
PROF-001
```

---

# Ready State

```text
No FAIL Results
```

Returns:

```text
READY
```

---

# Blocked State

```text
One Or More FAIL Results
```

Returns:

```text
BLOCKED
```

---

# Provisioning Gate

```python
start_button.setEnabled(
    readiness_result.ready
)
```

---

# End of READINESS_ENGINE.md