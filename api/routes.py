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
        SELECT id, start_time, end_time, duration_seconds, status, direction
        FROM train_events
        ORDER BY start_time DESC
        LIMIT 10
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

@api_bp.route("/api/trains_per_dow")
def trains_per_dow():
    # https://mariadb.com/docs/server/reference/sql-functions/date-time-functions/dayofweek
    # because using DAYOFWEEK gives monday=0 (stupid), let's add+mod to get sunday=0
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT 
            (DAYOFWEEK(CONVERT_TZ(start_time, 'UTC', 'America/Chicago')) + 6) % 7 AS day_of_week,
            COUNT(*) AS train_count
        FROM train_events
        GROUP BY day_of_week
        ORDER BY day_of_week
    """)
    rows = cur.fetchall()
    conn.close()
    
    # format it into a dict before returning
    dow_array = [0,0,0,0,0,0,0]
    for row in rows:
        day = row["day_of_week"] # 0=Sunday
        count = row["train_count"]
        dow_array[day] = count

    return jsonify(dow_array)
