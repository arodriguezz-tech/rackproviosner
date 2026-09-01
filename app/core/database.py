"""SQLite connection factories and schema initialization.

Layer rule: this module should depend only on lower-level modules documented in ARCHITECTURE.md.
"""

import sqlite3
from datetime import datetime, timezone
from .paths import DATA
INV_DB=DATA/"inventory.db"; APP_DB=DATA/"provisioning.db"
def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")
def connect(path):
    c=sqlite3.connect(path); c.row_factory=sqlite3.Row; c.execute("PRAGMA foreign_keys=ON"); return c
def inventory_connection(): return connect(INV_DB)
def app_connection(): return connect(APP_DB)
def initialize():
    with inventory_connection() as c:
        c.executescript("""CREATE TABLE IF NOT EXISTS racks(rack_serial TEXT PRIMARY KEY,rack_sku TEXT NOT NULL,rack_bom TEXT,rack_asset_tag TEXT,created_at TEXT NOT NULL,modified_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS devices(id INTEGER PRIMARY KEY AUTOINCREMENT,rack_serial TEXT NOT NULL REFERENCES racks(rack_serial) ON DELETE CASCADE,role TEXT NOT NULL CHECK(role IN ('MX','NS1','NS2')),model TEXT,serial_number TEXT,normalized_serial TEXT,mac_address TEXT,normalized_mac TEXT,notes TEXT,UNIQUE(rack_serial,role));
        CREATE INDEX IF NOT EXISTS idx_device_serial ON devices(normalized_serial); CREATE INDEX IF NOT EXISTS idx_device_mac ON devices(normalized_mac);""")
    with app_connection() as c:
        c.executescript("""CREATE TABLE IF NOT EXISTS sku(sku TEXT PRIMARY KEY,description TEXT,current_major INTEGER NOT NULL DEFAULT 1,current_minor INTEGER NOT NULL DEFAULT 0,modified_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS sku_content(sku TEXT PRIMARY KEY REFERENCES sku(sku) ON DELETE CASCADE,mx_text TEXT NOT NULL DEFAULT '',ns1_text TEXT NOT NULL DEFAULT '',ns2_text TEXT NOT NULL DEFAULT '',notes TEXT NOT NULL DEFAULT '',mx_model TEXT NOT NULL DEFAULT '',ns1_model TEXT NOT NULL DEFAULT '',ns2_model TEXT NOT NULL DEFAULT '');
        CREATE TABLE IF NOT EXISTS sku_revision(id INTEGER PRIMARY KEY AUTOINCREMENT,sku TEXT NOT NULL,major INTEGER NOT NULL,minor INTEGER NOT NULL,revision_type TEXT NOT NULL,trigger TEXT,change_summary TEXT,created_at TEXT NOT NULL,archive_path TEXT,checksum TEXT);
        CREATE TABLE IF NOT EXISTS jobs(id INTEGER PRIMARY KEY AUTOINCREMENT,rack_serial TEXT,rack_position TEXT,rack_sku TEXT,started_at TEXT,ended_at TEXT,status TEXT,block_reason TEXT);""")
