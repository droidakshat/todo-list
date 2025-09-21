import os
import sqlite3
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import datetime

# Remove old database if exists 
if os.path.exists('example.db'):
    os.remove('example.db')

# Create table after
def init_db():
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
    conn.close()

init_db()

app = FastAPI()

#initiate db connection
def get_db():
    return sqlite3.connect('example.db')

#pydantic model for tasks
class Task(BaseModel):
    id: int | None = None
    title: str
    description: str = ""
    completed: bool = False
    created_date: str | None = None

#api endpoint to create a task
@app.post("/tasks/create", response_model=Task)
def create_task(task: Task):
    created_date = datetime.datetime.now().isoformat()
    task.completed = False
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description, completed, created_date) VALUES (?, ?, ?, ?)",
        (task.title, task.description, int(task.completed), created_date)
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return Task(id=task_id, title=task.title, description=task.description, completed=task.completed, created_date=created_date)

#api endpoint to get all tasks
@app.get("/tasks/", response_model=List[Task])
def get_all_tasks():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, completed, created_date FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return [
        Task(id=row[0], title=row[1], description=row[2], completed=bool(row[3]), created_date=row[4])
        for row in rows
    ]

#api endpoint to get task by id
@app.get("/tasks/{task_id}", response_model=Task)
def get_task_by_id(task_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, completed, created_date FROM tasks WHERE id=?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Task(id=row[0], title=row[1], description=row[2], completed=bool(row[3]), created_date=row[4])
    return {"error": "Task not found"}

#api endpoint to update task by id
@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: Task):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET title=?, description=?, completed=? WHERE id=?",
        (task.title, task.description, int(task.completed), task_id)
    )
    conn.commit()
    cursor.execute("SELECT created_date FROM tasks WHERE id=?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    created_date = row[0] if row else None
    return Task(id=task_id, title=task.title, description=task.description, completed=task.completed, created_date=created_date)

#api endpoint to delete task by id
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return {"message": "Task deleted"}

@app.get("/")
def read_root():
    return {"message": "Server is running"}