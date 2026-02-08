import datetime
import os

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

# File logging (volume mounted)
LOG_FILE = os.environ.get("LOG_FILE", "/logs/logs.txt")

# Postgres connection settings (from Compose env)
DB_HOST = os.environ.get("DB_HOST", "db")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "loggerdb")
DB_USER = os.environ.get("DB_USER", "loggeruser")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")


def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/db-check", methods=["GET"])
def db_check():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()
        return jsonify({"db": "ok"})
    except Exception as e:
        return jsonify({"db": "error", "detail": str(e)}), 500


@app.route("/log", methods=["POST"])
def log():
    msg = request.form.get("message", "").strip()
    if not msg:
        return "Message is required", 400

    timestamp = str(datetime.datetime.now())

    # 1) Write to Postgres (durable + queryable)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO logs (message) VALUES (%s);",
        (f"[{timestamp}] {msg}",),
    )
    conn.commit()
    cur.close()
    conn.close()

    # 2) Also append to file (simple persistence comparison)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")

    return "Message logged to PostgreSQL + file ✅"


@app.route("/recent", methods=["GET"])
def recent():
    # Recent from Postgres
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, message, created_at FROM logs "
        "ORDER BY id DESC LIMIT 10;"
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    data = [
        {"id": r[0], "message": r[1], "created_at": str(r[2])}
        for r in rows
    ]
    return jsonify(data)


@app.route("/recent-file", methods=["GET"])
def recent_file():
    # Read last ~10 lines from the file log (simple approach)
    if not os.path.exists(LOG_FILE):
        return jsonify([])

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()[-10:]

    return jsonify([line.strip() for line in lines])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
