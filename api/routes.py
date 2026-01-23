from flask import Blueprint, jsonify
from database import get_conn

api_bp = Blueprint("api", __name__)

@api_bp.route("/api/active")
def active():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT EXISTS (
            SELECT 1 FROM train_events WHERE status = 'OPEN'
        )
    """)
    active = bool(cur.fetchone()[0])
    conn.close()
    return jsonify(active=active)

@api_bp.route("/api/recent_trains")
def recent_trains():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT id, start_time, end_time, duration_seconds, status
        FROM train_events
        ORDER BY start_time DESC
        LIMIT 5
    """)
    rows = cur.fetchall()
    conn.close()

    # Convert datetimes to string so JSON can handle them
    for row in rows:
        if row["start_time"]:
            row["start_time"] = row["start_time"].strftime("%Y-%m-%d %H:%M:%S")
        if row["end_time"]:
            row["end_time"] = row["end_time"].strftime("%Y-%m-%d %H:%M:%S")
    
    return jsonify(rows)
