import sqlite3

conn = sqlite3.connect("students.db")

cursor = conn.cursor()

# Students table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    cgpa REAL,
    aptitude INTEGER,
    communication INTEGER,
    projects INTEGER,
    internships INTEGER,
    certifications INTEGER,
    dsa INTEGER,
    probability REAL,
    result TEXT
)
""")

# Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

conn.commit()
conn.close()

print("Database Created Successfully!")