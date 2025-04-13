import sqlite3

conn = sqlite3.connect("db/storage.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def create_user_if_not_exists(telegram_id):
    cursor.execute("SELECT * FROM users WHERE id = ?", (telegram_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (id) VALUES (?)", (telegram_id,))
        conn.commit()

def update_user_name(telegram_id, name):
    cursor.execute("UPDATE users SET name = ? WHERE id = ?", (name, telegram_id))
    conn.commit()

def get_user_data(telegram_id):
    cursor.execute("SELECT * FROM users WHERE id = ?", (telegram_id,))
    return cursor.fetchone()

def create_medicine_if_not_exists(telegram_id, medicine_name): 
    try:
        cursor.execute("SELECT * FROM user_medicines WHERE user_id = ? AND name = ?", (telegram_id, medicine_name))
        medicine = cursor.fetchone()
        
        if not medicine:
            cursor.execute("INSERT INTO user_medicines (user_id, name) VALUES (?, ?)", (telegram_id, medicine_name))
            conn.commit()
            return "Medicine added successfully!"  # Success message
        else:
            return "This medicine is already in your list."  # If medicine exists
    except sqlite3.Error as e:
        conn.rollback()
        return f"A database error has occurred: {e}"  # Return error message

def get_medicines(telegram_id):
    cursor.execute("SELECT * FROM user_medicines WHERE user_id = ?", (telegram_id,))
    return cursor.fetchall()

# Reminders

def create_reminder_if_not_exists(user_id, medicine_id, time, dose, label=None):
        
    try:
        cursor.execute("""
            SELECT id FROM reminders 
            WHERE user_id = ? AND medicine_id = ? AND time = ?
        """, (user_id, medicine_id, time))
        existing = cursor.fetchone()

        if existing:
            return "⚠️ You already have a reminder for this medicine at that time."
    
        cursor.execute("""
            INSERT INTO reminders (user_id, medicine_id, time, label, dose)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, medicine_id, time, label, dose))
        conn.commit()
        return '✅ Reminder added successfully!'
    except sqlite3.Error as e:
        conn.rollback()
        return f"Error adding reminder: {e}"
    
def get_reminders(user_id):
    cursor.execute("""
        SELECT r.time, r.label, r.dose, m.name
        FROM reminders r
        JOIN user_medicines m ON r.medicine_id = m.id
        WHERE r.user_id = ?
        ORDER BY r.time
    """, (user_id,))
    return cursor.fetchall()

def update_reminder(reminder_id, time=None, label=None):
    if not time and not label:
        return "Nothing to update."
    
    updates = []
    values = []
    if time:
        updates.append("time = ?")
        values.append(time)
    if label:
        updates.append("label = ?")
        values.append(label)

    values.append(reminder_id)
    sql = f"UPDATE reminders SET {', '.join(updates)} WHERE id = ?"
    
    try:
        cursor.execute(sql, tuple(values))
        conn.commit()
        return True
    except sqlite3.Error as e:
        conn.rollback()
        return f"Update error: {e}"

