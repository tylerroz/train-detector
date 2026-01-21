import mariadb
import sys

# fine to hardcode these for local testing
try:
    conn = mariadb.connect(
        user="traincam",
        password="unionpacific111",
        host="localhost",
        port=3306,
        database="train_data"

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()