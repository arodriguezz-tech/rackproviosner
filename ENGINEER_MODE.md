# ENGINEER_MODE.md

Version: Alpha v3

Status: Active

---

# Purpose

Provide diagnostics and troubleshooting information without changing provisioning decisions.

Engineer Mode influences:

```text
Visibility
```

Not:

```text
Provisioning Authority
```

---

# Technician Mode

Displays:

```text
Inventory Verified

Hardware Verified

Network Connections Verified

Ready To Provision
```

Never Displays:

```text
Commands

Event Names

Error Codes

SQL

Debug Data
```

---

# Engineer Mode

Additional Information:

```text
Rule Results

Block Codes

Diagnostics

LLDP Details

Inventory Match Details

Event Monitor

Revision History
```

---

# Readiness Details

Example:

```text
Inventory PASS

Discovery PASS

SKU FAIL

SKU-001

Expected SN4700
Found SN2700
```

---

# Event Monitor

Displays:

```text
inventory.saved

inventory.verified

readiness.evaluated
```

---

# LLDP Diagnostics

Displays:

```text
Local Port

Neighbor Name

Neighbor MAC

Neighbor Port

Management IP
```

---

# Revision History

Displays:

```text
SKU

Version

Revision Type

Date
```

---

# End of ENGINEER_MODE.md