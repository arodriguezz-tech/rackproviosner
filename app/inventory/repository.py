"""SQLite inventory persistence and identity lookup.

The repository contains SQL and normalization only. Business validation and
application events belong in InventoryService.
"""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS racks(
    rack_serial TEXT PRIMARY KEY,
    rack_sku TEXT NOT NULL,
    rack_bom TEXT,
    rack_asset_tag TEXT,
    created_at TEXT NOT NULL,
    modified_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS devices(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rack_serial TEXT NOT NULL REFERENCES racks(rack_serial) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK(role IN ('MX','NS1','NS2')),
    model TEXT,
    serial_number TEXT,
    normalized_serial TEXT,
    mac_address TEXT,
    normalized_mac TEXT,
    notes TEXT,
    UNIQUE(rack_serial, role)
);
CREATE INDEX IF NOT EXISTS idx_device_serial ON devices(normalized_serial);
CREATE INDEX IF NOT EXISTS idx_device_mac ON devices(normalized_mac);
"""

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def normalize_serial(value: str) -> str:
    return "".join(value.strip().upper().split())

def normalize_mac(value: str) -> str:
    return "".join(ch for ch in value.upper() if ch in "0123456789ABCDEF")

class InventoryRepository:
    def __init__(self, database: str | Path):
        self.database = str(database)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(SCHEMA)

    def save(self, rack: dict, devices: list[dict]) -> None:
        timestamp = utcnow()
        with self.connect() as connection:
            connection.execute(
                """INSERT INTO racks(rack_serial,rack_sku,rack_bom,rack_asset_tag,created_at,modified_at)
                VALUES(?,?,?,?,?,?)
                ON CONFLICT(rack_serial) DO UPDATE SET
                    rack_sku=excluded.rack_sku,
                    rack_bom=excluded.rack_bom,
                    rack_asset_tag=excluded.rack_asset_tag,
                    modified_at=excluded.modified_at""",
                (rack["rack_serial"], rack["rack_sku"], rack.get("rack_bom", ""),
                 rack.get("rack_asset_tag", ""), timestamp, timestamp),
            )
            for device in devices:
                serial = device.get("serial", "").strip()
                mac = device.get("mac", "").strip()
                connection.execute(
                    """INSERT INTO devices(
                        rack_serial,role,model,serial_number,normalized_serial,
                        mac_address,normalized_mac,notes)
                    VALUES(?,?,?,?,?,?,?,?)
                    ON CONFLICT(rack_serial,role) DO UPDATE SET
                        model=excluded.model,
                        serial_number=excluded.serial_number,
                        normalized_serial=excluded.normalized_serial,
                        mac_address=excluded.mac_address,
                        normalized_mac=excluded.normalized_mac,
                        notes=excluded.notes""",
                    (rack["rack_serial"], device["role"], device.get("model", ""), serial,
                     normalize_serial(serial) if serial else None, mac,
                     normalize_mac(mac) if mac else None, device.get("notes", "")),
                )

    def get_rack(self, rack_serial: str):
        with self.connect() as connection:
            rack = connection.execute(
                "SELECT * FROM racks WHERE rack_serial=?", (rack_serial,)
            ).fetchone()
            devices = connection.execute(
                "SELECT * FROM devices WHERE rack_serial=? ORDER BY role", (rack_serial,)
            ).fetchall()
        return rack, devices

    def delete_rack(self, rack_serial: str) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM racks WHERE rack_serial=?", (rack_serial,))

    def identity_matches(self, rack_serial: str, serial: str, mac: str):
        serial_key = normalize_serial(serial) if serial else ""
        mac_key = normalize_mac(mac) if mac else ""
        with self.connect() as connection:
            serial_row = connection.execute(
                "SELECT role FROM devices WHERE rack_serial=? AND normalized_serial=?",
                (rack_serial, serial_key),
            ).fetchone() if serial_key else None
            mac_row = connection.execute(
                "SELECT role FROM devices WHERE rack_serial=? AND normalized_mac=?",
                (rack_serial, mac_key),
            ).fetchone() if mac_key else None

        if serial_row and mac_row and serial_row["role"] != mac_row["role"]:
            return "CONFLICT", None, "Serial and MAC map to different roles"
        match = serial_row or mac_row
        if match:
            evidence = "serial+MAC" if serial_row and mac_row else "serial" if serial_row else "MAC"
            return "VERIFIED", match["role"], f"Matched by {evidence}"
        return "UNKNOWN", None, "No serial or MAC match for this rack"
