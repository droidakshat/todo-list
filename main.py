import sqlite3
from fastapi import FastAPI

# Connect to SQLite database (creates file if it doesn't exist)
conn = sqlite3.connect('example.db')
cursor = conn.cursor()

# Create a table for tasks
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    completed INTEGER NOT NULL DEFAULT 0
)
''')
conn.commit()

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Server is running"}