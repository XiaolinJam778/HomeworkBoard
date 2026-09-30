import sqlite3
from datetime import datetime
from pathlib import Path


# -------------------------
# Database paths
# -------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "homework.db"


# -------------------------
# Connection
# -------------------------

def get_connection():
    """Connect to the HomeworkBoard SQLite database."""
    DATA_DIR.mkdir(exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    # 查询结果可以通过字段名访问
    connection.row_factory = sqlite3.Row

    return connection


# -------------------------
# Database initialization
# -------------------------

def create_tables():
    """Create database tables if they do not already exist."""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course TEXT NOT NULL,
            title TEXT NOT NULL,
            due_date TEXT NOT NULL,
            due_time TEXT,
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            completed_at TEXT
        )
    """)

    connection.commit()
    connection.close()


# -------------------------
# CREATE
# -------------------------

def add_assignment(course, title, due_date, due_time=None):
    """Add a new assignment."""

    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().isoformat(timespec="seconds")

    cursor.execute("""
        INSERT INTO assignments (
            course,
            title,
            due_date,
            due_time,
            completed,
            created_at
        )
        VALUES (?, ?, ?, ?, 0, ?)
    """, (
        course,
        title,
        due_date,
        due_time,
        created_at
    ))

    assignment_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return assignment_id


# -------------------------
# READ
# -------------------------

def get_assignments():
    """Return all assignments ordered by deadline."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM assignments
        ORDER BY
            completed ASC,
            due_date ASC,
            due_time ASC
    """)

    assignments = cursor.fetchall()

    connection.close()

    return assignments


def get_assignment(assignment_id):
    """Return one assignment by ID."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM assignments
        WHERE id = ?
    """, (assignment_id,))

    assignment = cursor.fetchone()

    connection.close()

    return assignment


# -------------------------
# UPDATE
# -------------------------

def update_assignment(
    assignment_id,
    course,
    title,
    due_date,
    due_time=None
):
    """Update an existing assignment."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE assignments
        SET
            course = ?,
            title = ?,
            due_date = ?,
            due_time = ?
        WHERE id = ?
    """, (
        course,
        title,
        due_date,
        due_time,
        assignment_id
    ))

    connection.commit()
    connection.close()


def set_assignment_completed(assignment_id, completed=True):
    """Mark an assignment as completed or incomplete."""

    connection = get_connection()
    cursor = connection.cursor()

    if completed:
        completed_value = 1
        completed_at = datetime.now().isoformat(timespec="seconds")
    else:
        completed_value = 0
        completed_at = None

    cursor.execute("""
        UPDATE assignments
        SET
            completed = ?,
            completed_at = ?
        WHERE id = ?
    """, (
        completed_value,
        completed_at,
        assignment_id
    ))

    connection.commit()
    connection.close()


# -------------------------
# DELETE
# -------------------------

def delete_assignment(assignment_id):
    """Delete an assignment."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM assignments
        WHERE id = ?
    """, (assignment_id,))

    connection.commit()
    connection.close()

def get_visible_assignments():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM assignments
        WHERE 
            completed = 0
            OR completed_at IS NULL
            OR date(completed_at) = date('now', 'localtime')
        ORDER BY
            completed ASC,
            due_date ASC,
            COALESCE(due_time, '23:59') ASC
    """)
    assignments = cursor.fetchall()
    connection.close()

    return assignments

# -------------------------
# Run directly
# -------------------------

if __name__ == "__main__":
    create_tables()
    print(f"Database initialized: {DB_PATH}")