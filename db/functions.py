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
        cursor.execute(
            "SELECT * FROM user_medicines WHERE user_id = ? AND name = ?",
            (telegram_id, medicine_name),
        )
        medicine = cursor.fetchone()

        if not medicine:
            cursor.execute(
                "INSERT INTO user_medicines (user_id, name) VALUES (?, ?)",
                (telegram_id, medicine_name),
            )
            conn.commit()
            return "Лекарство успешно добавлено!"  # Success message
        else:
            return "Это лекарство уже есть в списке."  # If medicine exists
    except sqlite3.Error as e:
        conn.rollback()
        return f"A database error has occurred: {e}"  # Return error message


def get_medicines(telegram_id):
    cursor.execute("SELECT * FROM user_medicines WHERE user_id = ?", (telegram_id,))
    return cursor.fetchall()


# Reminders


def create_reminder_with_schedule(user_id, medicine_id, days, time, dose, label=None):
    try:
        # Create a new reminder no matter what
        new_reminder_id = create_reminder(user_id, medicine_id, time, dose, label)

        for day in days:
            # Check if there's already a schedule at this day/time for this medicine
            old_reminder_id = get_reminder_id_for_schedule(
                user_id, medicine_id, day, time
            )

            if old_reminder_id:
                # Reassign the existing schedule to the new reminder
                cursor.execute(
                    """
                    UPDATE reminder_schedule
                    SET reminder_id = ?
                    WHERE reminder_id = ? AND day_of_week = ? AND time = ?
                """,
                    (new_reminder_id, old_reminder_id, day, time),
                )

                # Check if the old reminder has any schedules left
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM reminder_schedule
                    WHERE reminder_id = ?
                """,
                    (old_reminder_id,),
                )
                count = cursor.fetchone()[0]

                if count == 0:
                    cursor.execute(
                        "DELETE FROM reminders WHERE id = ?", (old_reminder_id,)
                    )

            else:
                # No conflict, just create a new schedule entry
                create_reminder_schedule(new_reminder_id, day, time)

        conn.commit()
        return "✅ Напоминание успешно добавлено!"

    except sqlite3.Error as e:
        conn.rollback()
        return f"❌ Ошибка при добавлении напоминания: {e}"


def get_reminder_id_for_schedule(user_id, medicine_id, day, time):
    cursor.execute(
        """
        SELECT r.id FROM reminders r
        JOIN reminder_schedule rs ON r.id = rs.reminder_id
        WHERE r.user_id = ? AND r.medicine_id = ? AND rs.day_of_week = ? AND rs.time = ?
    """,
        (user_id, medicine_id, day, time),
    )
    row = cursor.fetchone()
    return row[0] if row else None


def create_reminder(user_id, medicine_id, time, dose, label=None):
    """Insert the reminder record into the reminders table."""
    cursor.execute(
        """
        INSERT INTO reminders (user_id, medicine_id, label, time, dose)
        VALUES (?, ?, ?, ?, ?)
    """,
        (user_id, medicine_id, label, time, dose),
    )
    reminder_id = cursor.lastrowid
    conn.commit()
    return reminder_id


def create_reminder_schedule(reminder_id, day, time, is_one_time=False):
    cursor.execute(
        """
        INSERT INTO reminder_schedule (reminder_id, day_of_week, time, is_one_time)
        VALUES (?, ?, ?, ?)
    """,
        (reminder_id, day, time, is_one_time),
    )
    conn.commit()


def get_reminders(user_id):
    cursor.execute(
        """
        SELECT r.id, r.time, r.label, r.dose, m.name
        FROM reminders r
        JOIN user_medicines m ON r.medicine_id = m.id
        WHERE r.user_id = ?
        ORDER BY r.time
    """,
        (user_id,),
    )
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


def create_user_if_not_exists(telegram_id):
    cursor.execute("SELECT * FROM users WHERE id = ?", (telegram_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (id) VALUES (?)", (telegram_id,))
        conn.commit()


def get_reminders_with_schedule(telegram_id):
    cursor.execute(
        """
        SELECT r.id, m.name, r.dose, rs.day_of_week, r.time, rs.is_one_time
        FROM reminders r
        JOIN user_medicines m ON r.medicine_id = m.id
        JOIN reminder_schedule rs ON rs.reminder_id = r.id
        WHERE r.user_id = ?
        ORDER BY r.time
    """,
        (telegram_id,),
    )

    reminders = cursor.fetchall()
    return reminders


def delete_medicine(user_id, medicine_id):
    try:
        cursor.execute(
            """
            DELETE FROM user_medicines
            WHERE user_id = ? AND id = ?
        """,
            (user_id, medicine_id),
        )

        conn.commit()

        if cursor.rowcount > 0:
            return "✅ Лекарство успешно удалено."
        else:
            return "⚠️ Лекарство не найдено или не принадлежит вам."

    except sqlite3.Error as e:
        conn.rollback()
        return f"❌ Ошибка при удалении лекарства: {e}"


def delete_reminder(reminder_id: int):
    try:
        cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        conn.commit()
        return "Напоминание успешно удалено."
    except Exception as e:
        conn.rollback()
        return f"Ошибка при удалении напоминания: {e}"


def delete_reminder_schedule(reminder_id: int):
    try:
        cursor.execute(
            "DELETE FROM reminder_schedule WHERE reminder_id = ?", (reminder_id,)
        )
        conn.commit()
        return "Напоминание для расписания удалено."
    except Exception as e:
        conn.rollback()
        return f"Ошибка при удалении расписания: {e}"


def get_reminders_by_day_and_time(day_of_week: str, time: str):

    query = """
        SELECT 
            u.id AS telegram_id, 
            m.name AS medicine_name, 
            r.dose AS dose, 
            r.id AS reminder_id, 
            rs.is_one_time AS is_one_time
        FROM reminders r
        JOIN reminder_schedule rs ON rs.reminder_id = r.id
        JOIN user_medicines m ON r.medicine_id = m.id
        JOIN users u ON r.user_id = u.id
        WHERE rs.day_of_week = ? AND rs.time = ?
    """
    cursor.execute(query, (day_of_week, time))
    result = cursor.fetchall()
    
    return result

def delete_one_time_reminder_schedules_by_reminder_id(reminder_id):
    cursor.execute("""
        DELETE FROM reminder_schedule
        WHERE reminder_id = ? AND is_one_time = 1
    """, (reminder_id,))
    conn.commit()
    print(f"Deleted one-time reminder schedules for reminder_id: {reminder_id}")

def get_postponed_reminders(telegram_id):
    cursor.execute(
        """
        SELECT r.id, m.name, r.dose, rs.day_of_week, rs.time
        FROM reminders r
        JOIN user_medicines m ON r.medicine_id = m.id
        JOIN reminder_schedule rs ON rs.reminder_id = r.id
        WHERE r.user_id = ? AND rs.is_one_time = 1
        ORDER BY rs.time
        """,
        (telegram_id,)
    )
    return cursor.fetchall()

def create_medical_history_entry_now(user_id, medicine_name, dose, status, reminder_id, time=None):
    from datetime import datetime

    now = datetime.now()
    if not time:
        taken_at = now.isoformat(timespec='minutes')
    else:
        taken_at = time
    day_of_week = now.strftime("%a")  # e.g., 'Mon'

    cursor.execute("""
        INSERT INTO medicine_intake_history (user_id, medicine_name, dose, taken_at, day_of_week, status, reminder_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, medicine_name, dose, taken_at, day_of_week, status, reminder_id))
    
    conn.commit()


def get_medicine_history_for_user(user_id, limit=30):
    cursor.execute("""
        SELECT medicine_name, dose, taken_at, day_of_week, status
        FROM medicine_intake_history
        WHERE user_id = ?
        ORDER BY taken_at DESC
        LIMIT ?
    """, (user_id, limit))

    result = cursor.fetchall()

    return result

def create_reminder_message(reminder_id, message_id, sent_at):
    cursor.execute("""
        INSERT INTO reminder_messages (reminder_id, message_id, sent_at)
        VALUES (?, ?, ?)
    """, (reminder_id, message_id, sent_at))
    conn.commit()

def delete_reminder_message(message_id):
    cursor.execute("""
        DELETE FROM reminder_messages
        WHERE message_id = ?
    """, (message_id,))
    conn.commit()

def get_overdue_reminders(time_limit):
    cursor.execute("""
        SELECT rm.id, rm.reminder_id, rm.message_id, rm.sent_at, r.user_id, m.name, r.dose
        FROM reminder_messages rm
        JOIN reminders r ON rm.reminder_id = r.id
        JOIN user_medicines m ON r.medicine_id = m.id
        LEFT JOIN medicine_intake_history h ON h.reminder_id = rm.reminder_id
        WHERE rm.sent_at <= ? AND h.status IS NULL
    """, (time_limit,))
    
    return cursor.fetchall()