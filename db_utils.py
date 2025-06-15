import sqlite3
from datetime import datetime

DB_NAME = "pool.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            entry_time TEXT NOT NULL,
            exit_time TEXT,
            duration REAL,
            charge INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def log_entry(name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO logs (name, entry_time) VALUES (?, ?)", (name, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def log_exit(name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, entry_time FROM logs WHERE name=? AND exit_time IS NULL", (name,))
    row = c.fetchone()
    if row:
        log_id, entry_time = row
        exit_time = datetime.now()
        duration = (exit_time - datetime.fromisoformat(entry_time)).total_seconds() / 3600
        charge = int((duration // 1 + 1) * 100)
        c.execute("""
            UPDATE logs 
            SET exit_time=?, duration=?, charge=? 
            WHERE id=?
        """, (exit_time.isoformat(), round(duration, 2), charge, log_id))
    conn.commit()
    conn.close()

def get_active_swimmers():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name, entry_time FROM logs WHERE exit_time IS NULL")
    data = c.fetchall()
    conn.close()
    return data

def get_today_logs():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    today = datetime.now().date().isoformat()
    c.execute("""
        SELECT name, entry_time, exit_time, duration, charge 
        FROM logs 
        WHERE DATE(entry_time)=?
        AND exit_time IS NOT NULL
    """, (today,))
    data = c.fetchall()
    conn.close()
    return data

def get_all_log_dates():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT DISTINCT DATE(entry_time) FROM logs WHERE exit_time IS NOT NULL")
    dates = [row[0] for row in c.fetchall()]
    conn.close()
    return dates

def get_logs_by_date(date_str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT name, entry_time, exit_time, duration, charge 
        FROM logs 
        WHERE DATE(entry_time)=?
    """, (date_str,))
    data = c.fetchall()
    conn.close()
    return data
