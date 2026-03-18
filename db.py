"""
db.py — Query helpers for KONE energy SQLite database.
"""

import sqlite3
import pandas as pd

DB_PATH = "data/kone_energy.db"


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_buildings() -> pd.DataFrame:
    with _conn() as conn:
        return pd.read_sql("SELECT * FROM buildings ORDER BY name", conn)


def get_elevators(building_id: str = None) -> pd.DataFrame:
    with _conn() as conn:
        q = "SELECT * FROM elevators"
        params = []
        if building_id:
            q += " WHERE building_id = ?"
            params.append(building_id)
        return pd.read_sql(q, conn, params=params)


def get_daily_energy(building_id: str = None, days: int = 30) -> pd.DataFrame:
    with _conn() as conn:
        where = "WHERE timestamp >= date('now', ?)"
        params = [f"-{days} days"]
        if building_id and building_id != "ALL":
            where += " AND building_id = ?"
            params.append(building_id)
        q = f"""
            SELECT
                date(timestamp) AS day,
                building_id,
                SUM(kwh) AS total_kwh,
                SUM(regen_kwh) AS total_regen_kwh,
                SUM(standby_kwh) AS total_standby_kwh,
                SUM(trips) AS total_trips,
                AVG(avg_load_pct) AS avg_load
            FROM energy_readings
            {where}
            GROUP BY day, building_id
            ORDER BY day
        """
        return pd.read_sql(q, conn, params=params)


def get_hourly_profile(building_id: str = None, days: int = 30) -> pd.DataFrame:
    """Average energy by hour-of-day."""
    with _conn() as conn:
        where = "WHERE timestamp >= date('now', ?)"
        params = [f"-{days} days"]
        if building_id and building_id != "ALL":
            where += " AND building_id = ?"
            params.append(building_id)
        q = f"""
            SELECT
                CAST(strftime('%H', timestamp) AS INTEGER) AS hour,
                AVG(kwh) AS avg_kwh,
                AVG(trips) AS avg_trips
            FROM energy_readings
            {where}
            GROUP BY hour
            ORDER BY hour
        """
        return pd.read_sql(q, conn, params=params)


def get_building_summary() -> pd.DataFrame:
    with _conn() as conn:
        q = """
            SELECT
                b.id,
                b.name,
                b.city,
                b.elevator_count,
                ROUND(SUM(e.kwh), 2) AS total_kwh,
                ROUND(SUM(e.regen_kwh), 2) AS total_regen_kwh,
                ROUND(AVG(e.avg_load_pct), 1) AS avg_load_pct,
                SUM(e.trips) AS total_trips
            FROM buildings b
            JOIN energy_readings e ON b.id = e.building_id
            WHERE e.timestamp >= date('now', '-30 days')
            GROUP BY b.id
            ORDER BY total_kwh DESC
        """
        return pd.read_sql(q, conn)


def get_elevator_ranking(building_id: str = None, days: int = 30) -> pd.DataFrame:
    with _conn() as conn:
        where = "WHERE r.timestamp >= date('now', ?)"
        params = [f"-{days} days"]
        if building_id and building_id != "ALL":
            where += " AND r.building_id = ?"
            params.append(building_id)
        q = f"""
            SELECT
                r.elevator_id,
                el.model,
                el.install_year,
                b.name AS building_name,
                ROUND(SUM(r.kwh), 2) AS total_kwh,
                ROUND(SUM(r.regen_kwh), 2) AS regen_kwh,
                SUM(r.trips) AS trips,
                ROUND(AVG(r.avg_load_pct), 1) AS avg_load,
                ROUND(SUM(r.kwh) / NULLIF(SUM(r.trips), 0), 4) AS kwh_per_trip
            FROM energy_readings r
            JOIN elevators el ON r.elevator_id = el.id
            JOIN buildings b ON r.building_id = b.id
            {where}
            GROUP BY r.elevator_id
            ORDER BY total_kwh DESC
        """
        return pd.read_sql(q, conn, params=params)
