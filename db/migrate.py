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
CREATE TABLE IF NOT EXISTS events (
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
    label TEXT,
    dose TEXT,
    time TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (medicine_id) REFERENCES user_medicines(id) ON DELETE CASCADE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS reminder_schedule (
    id INTEGER PRIMARY KEY,
    reminder_id INTEGER,
    is_one_time BOOLEAN DEFAULT 0,
    day_of_week TEXT,      -- e.g., 'Monday', 'Tuesday', etc.
    time TEXT,             -- HH:MM
    FOREIGN KEY (reminder_id) REFERENCES reminders(id) ON DELETE CASCADE
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS medicine_intake_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    reminder_id INTEGER NOT NULL,
    medicine_name TEXT NOT NULL,
    dose TEXT,
    taken_at TEXT NOT NULL,
    day_of_week TEXT,
    status TEXT,
    FOREIGN KEY (reminder_id) REFERENCES reminders(id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminder_messages (
        id INTEGER PRIMARY KEY,
        reminder_id INTEGER,
        message_id INTEGER,
        sent_at TEXT,
        FOREIGN KEY (reminder_id) REFERENCES reminders(id) ON DELETE CASCADE
    );
""")

conn.commit()