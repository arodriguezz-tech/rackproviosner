"""Technician-friendly readiness language.

Internal rules and error codes must not expose commands or implementation
terminology in Technician Mode.
"""

CHECK_LABELS = {
    "inventory": "Inventory information verified",
    "discovery": "Switch identified",
    "sku_model": "Hardware matches rack configuration",
    "lldp": "Required network connections detected",
    "profile": "Configuration is available",
}

BLOCK_MESSAGES = {
    "DISC-001": "The switch could not be identified completely.",
    "INV-001": "Inventory information could not be verified.",
    "SKU-001": "The detected hardware does not match this rack configuration.",
    "LLDP-001": "Required network connections were not detected.",
    "PROF-001": "The required switch configuration is unavailable.",
}

STATUS_LABELS = {
    "PASS": "Verified",
    "WARNING": "Needs review",
    "FAIL": "Blocked",
    "PENDING": "Waiting",
}
