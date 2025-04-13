import sqlite3

conn = sqlite3.connect("db/storage.db")  # Creates data.db or connects to it
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    timezone TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_medicines (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    name TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, name)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS meals (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    name TEXT,
    time TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    medicine_id INTEGER,
    time TEXT,
    label TEXT,
    dose TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (medicine_id) REFERENCES user_medicines(id) ON DELETE CASCADE,
    UNIQUE(user_id, medicine_id, time)
)
""")

conn.commit()