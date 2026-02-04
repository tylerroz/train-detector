import mysql.connector
from datetime import datetime, timezone

DB_CONFIG = {
    "host": "localhost", # database and detector on the same machine
    "user": "traincam",
    "password": "unionpacific111",
    "database": "train_data",
    "autocommit": False
}

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

def now_utc():
    return datetime.now(timezone.utc)

def start_train_event():
    conn = get_conn()
    cur = conn.cursor()

    # Ensure no open train exists
    cur.execute("""
        SELECT id FROM train_events
        WHERE status = 'OPEN'
        LIMIT 1
    """)
    if cur.fetchone():
        conn.close()
        return

    cur.execute("""
        INSERT INTO train_events (start_time, status)
        VALUES (%s, 'OPEN')
    """, (now_utc(),))

    conn.commit()
    conn.close()

def end_train_event(direction=None):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT id, start_time
        FROM train_events
        WHERE status = 'OPEN'
        ORDER BY start_time DESC
        LIMIT 1
    """)
    row = cur.fetchone()

    if not row:
        conn.close()
        return

    end = now_utc()
    start = row["start_time"].replace(tzinfo=timezone.utc)
    duration = int((end - start).total_seconds())

    cur.execute("""
        UPDATE train_events
        SET end_time = %s,
            duration_seconds = %s,
            status = 'CLOSED',
            direction = %s
        WHERE id = %s
    """, (end, duration, direction.name, row["id"]))

    conn.commit()
    conn.close()

def recover_open_events():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT id, start_time
        FROM train_events
        WHERE status = 'OPEN'
    """)
    rows = cur.fetchall()

    for row in rows:
        start = row["start_time"].replace(tzinfo=timezone.utc)
        end = now_utc()
        duration = int((end - start).total_seconds())

        cur.execute("""
            UPDATE train_events
            SET end_time = %s,
                duration_seconds = %s,
                status = 'ABORTED'
            WHERE id = %s
        """, (end, duration, row["id"]))

    conn.commit()
    conn.close()