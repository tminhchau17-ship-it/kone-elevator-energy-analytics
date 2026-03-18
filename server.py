"""
server.py — KONE Energy Analytics  |  Flask web server
Run:  python server.py
Open: http://localhost:5000
"""

from flask import Flask, jsonify, render_template, request
import db

app = Flask(__name__)

# ── Pages ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── API endpoints ─────────────────────────────────────────────────────────────

@app.route("/api/buildings")
def api_buildings():
    df = db.get_buildings()
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/kpis")
def api_kpis():
    bld  = request.args.get("building", "ALL")
    days = int(request.args.get("days", 30))
    df   = db.get_daily_energy(bld, days)
    if df.empty:
        return jsonify({})
    total_kwh   = round(df["total_kwh"].sum(), 1)
    regen_kwh   = round(df["total_regen_kwh"].sum(), 1)
    trips       = int(df["total_trips"].sum())
    avg_load    = round(float(df["avg_load"].mean()), 1)
    savings_pct = round(regen_kwh / total_kwh * 100 if total_kwh else 0, 1)
    return jsonify({
        "total_kwh":   total_kwh,
        "regen_kwh":   regen_kwh,
        "trips":       trips,
        "avg_load":    avg_load,
        "savings_pct": savings_pct,
    })


@app.route("/api/daily")
def api_daily():
    bld  = request.args.get("building", "ALL")
    days = int(request.args.get("days", 30))
    df   = db.get_daily_energy(bld, days)
    if df.empty:
        return jsonify({"labels": [], "consumed": [], "regen": []})
    agg = df.groupby("day").agg(
        total_kwh=("total_kwh", "sum"),
        total_regen_kwh=("total_regen_kwh", "sum"),
    ).reset_index()
    return jsonify({
        "labels":   agg["day"].tolist(),
        "consumed": [round(v, 2) for v in agg["total_kwh"].tolist()],
        "regen":    [round(v, 2) for v in agg["total_regen_kwh"].tolist()],
    })


@app.route("/api/hourly")
def api_hourly():
    bld  = request.args.get("building", "ALL")
    days = int(request.args.get("days", 30))
    df   = db.get_hourly_profile(bld, days)
    if df.empty:
        return jsonify({"labels": [], "kwh": [], "trips": []})
    return jsonify({
        "labels": [f"{int(h):02d}:00" for h in df["hour"].tolist()],
        "kwh":    [round(v, 4) for v in df["avg_kwh"].tolist()],
        "trips":  [round(v, 1) for v in df["avg_trips"].tolist()],
    })


@app.route("/api/buildings/summary")
def api_bld_summary():
    df = db.get_building_summary()
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/energy_split")
def api_energy_split():
    bld  = request.args.get("building", "ALL")
    days = int(request.args.get("days", 30))
    df   = db.get_daily_energy(bld, days)
    if df.empty:
        return jsonify({})
    consumed = round(float(df["total_kwh"].sum() - df["total_regen_kwh"].sum()), 1)
    regen    = round(float(df["total_regen_kwh"].sum()), 1)
    standby  = round(float(df["total_standby_kwh"].sum()), 1)
    return jsonify({"consumed": consumed, "regen": regen, "standby": standby})


@app.route("/api/elevators")
def api_elevators():
    bld  = request.args.get("building", "ALL")
    days = int(request.args.get("days", 30))
    df   = db.get_elevator_ranking(bld, days)
    return jsonify(df.to_dict(orient="records"))


if __name__ == "__main__":
    app.run(debug=False, port=5000)
