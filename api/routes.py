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
