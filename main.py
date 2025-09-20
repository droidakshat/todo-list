import sqlite3
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import datetime

conn = sqlite3.connect('example.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT 0,
    created_date TEXT NOT NULL
)
''')
conn.commit()

app = FastAPI()

class Task(BaseModel):
    id: int | None = None
    title: str
    description: str = ""
    completed: bool = False
    created_date: str | None = None

@app.post("/tasks/create", response_model=Task)
def create_task(task: Task):
    created_date = datetime.datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO tasks (title, description, completed, created_date) VALUES (?, ?, ?, ?)",
        (task.title, task.description, int(task.completed), created_date)
    )
    conn.commit()
    task_id = cursor.lastrowid
    return Task(id=task_id, title=task.title, description=task.description, completed=task.completed, created_date=created_date)

@app.get("/tasks/", response_model=List[Task])
def get_all_tasks():
    cursor.execute("SELECT id, title, description, completed, created_date FROM tasks")
    rows = cursor.fetchall()
    return [
        Task(id=row[0], title=row[1], description=row[2], completed=bool(row[3]), created_date=row[4])
        for row in rows
    ]

@app.get("/tasks/{task_id}", response_model=Task)
def get_task_by_id(task_id: int):
    cursor.execute("SELECT id, title, description, completed, created_date FROM tasks WHERE id=?", (task_id,))
    row = cursor.fetchone()
    if row:
        return Task(id=row[0], title=row[1], description=row[2], completed=bool(row[3]), created_date=row[4])
    return {"error": "Task not found"}

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: Task):
    cursor.execute(
        "UPDATE tasks SET title=?, description=?, completed=? WHERE id=?",
        (task.title, task.description, int(task.completed), task_id)
    )
    conn.commit()
    # Fetch created_date for response
    cursor.execute("SELECT created_date FROM tasks WHERE id=?", (task_id,))
    row = cursor.fetchone()
    created_date = row[0] if row else None
    return Task(id=task_id, title=task.title, description=task.description, completed=task.completed, created_date=created_date)

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    return {"message": "Task deleted"}

@app.get("/")
def read_root():
    return {"message": "Server is running"}