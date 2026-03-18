"""
seed_db.py — Creates and populates the KONE energy SQLite database
with realistic simulated elevator energy consumption data.
"""

import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "data/kone_energy.db"

BUILDINGS = [
    {"id": "BLD-001", "name": "Helsinki HQ Tower", "city": "Helsinki", "floors": 32, "elevators": 6},
    {"id": "BLD-002", "name": "Espoo Innovation Hub", "city": "Espoo", "floors": 18, "elevators": 4},
    {"id": "BLD-003", "name": "Tampere Commerce Center", "city": "Tampere", "floors": 24, "elevators": 5},
    {"id": "BLD-004", "name": "Turku Harbor Building", "city": "Turku", "floors": 14, "elevators": 3},
    {"id": "BLD-005", "name": "Oulu Tech Campus", "city": "Oulu", "floors": 10, "elevators": 2},
]

ELEVATOR_MODELS = ["KONE MonoSpace 700", "KONE MiniSpace", "KONE TranSys", "KONE EcoDisc"]


def create_schema(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS buildings (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            floors INTEGER NOT NULL,
            elevator_count INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS elevators (
            id TEXT PRIMARY KEY,
            building_id TEXT NOT NULL,
            model TEXT NOT NULL,
            install_year INTEGER NOT NULL,
            capacity_kg INTEGER NOT NULL,
            FOREIGN KEY (building_id) REFERENCES buildings(id)
        );

        CREATE TABLE IF NOT EXISTS energy_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            elevator_id TEXT NOT NULL,
            building_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            kwh REAL NOT NULL,
            trips INTEGER NOT NULL,
            avg_load_pct REAL NOT NULL,
            standby_kwh REAL NOT NULL,
            regen_kwh REAL NOT NULL,
            FOREIGN KEY (elevator_id) REFERENCES elevators(id)
        );
    """)
    conn.commit()


def seed_buildings(conn):
    conn.executemany(
        "INSERT OR REPLACE INTO buildings VALUES (?, ?, ?, ?, ?)",
        [(b["id"], b["name"], b["city"], b["floors"], b["elevators"]) for b in BUILDINGS],
    )
    conn.commit()


def seed_elevators(conn):
    rows = []
    for b in BUILDINGS:
        for i in range(1, b["elevators"] + 1):
            eid = f"{b['id']}-ELV-{i:02d}"
            model = random.choice(ELEVATOR_MODELS)
            year = random.randint(2010, 2022)
            capacity = random.choice([630, 800, 1000, 1275])
            rows.append((eid, b["id"], model, year, capacity))
    conn.executemany(
        "INSERT OR REPLACE INTO elevators VALUES (?, ?, ?, ?, ?)", rows
    )
    conn.commit()
    return [r[0] for r in rows]


def seed_readings(conn, elevator_ids):
    """Generate hourly readings for the last 90 days."""
    rows = []
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    start = now - timedelta(days=90)

    for eid in elevator_ids:
        bid = "-".join(eid.split("-")[:2])
        building = next(b for b in BUILDINGS if b["id"] == bid)
        floors = building["floors"]

        current = start
        while current <= now:
            hour = current.hour
            # Traffic profile: peaks at 8-9, 12-13, 17-18
            if hour in (8, 9, 17, 18):
                base_trips = random.randint(30, 60)
                load = random.uniform(55, 85)
            elif hour in (12, 13):
                base_trips = random.randint(20, 40)
                load = random.uniform(45, 70)
            elif 7 <= hour <= 20:
                base_trips = random.randint(8, 25)
                load = random.uniform(25, 55)
            else:
                base_trips = random.randint(0, 5)
                load = random.uniform(10, 30)

            # Energy scales with trips, floors, and load
            kwh = round((base_trips * floors * 0.0008 * (load / 100)) + random.uniform(0.1, 0.4), 4)
            standby = round(random.uniform(0.05, 0.15), 4)
            regen = round(kwh * random.uniform(0.05, 0.20), 4)  # regenerative braking savings

            rows.append((
                eid, bid,
                current.strftime("%Y-%m-%d %H:%M:%S"),
                kwh, base_trips,
                round(load, 2), standby, regen
            ))
            current += timedelta(hours=1)

    conn.executemany(
        """INSERT INTO energy_readings
           (elevator_id, building_id, timestamp, kwh, trips, avg_load_pct, standby_kwh, regen_kwh)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        rows,
    )
    conn.commit()
    print(f"  Inserted {len(rows):,} energy readings.")


def run():
    import os
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    print("Creating schema...")
    create_schema(conn)
    print("Seeding buildings...")
    seed_buildings(conn)
    print("Seeding elevators...")
    elevator_ids = seed_elevators(conn)
    print(f"Seeding energy readings for {len(elevator_ids)} elevators...")
    seed_readings(conn, elevator_ids)
    conn.close()
    print("Database ready at", DB_PATH)


if __name__ == "__main__":
    run()
