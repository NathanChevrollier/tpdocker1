from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
import uuid
import os
import sqlite3
from contextlib import closing
from pathlib import Path

# Optional PostgreSQL support via psycopg when TODO_DB_URL is set
DB_URL = os.getenv("TODO_DB_URL")
USE_POSTGRES = bool(DB_URL)
if USE_POSTGRES:
    import psycopg  # type: ignore
    from psycopg.rows import dict_row  # type: ignore

DB_PATH = Path(os.getenv("TODO_DB_PATH", "data/todo.db"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_conn():
    if USE_POSTGRES:
        # autocommit for simple statements; dict_row returns dicts like sqlite Row
        return psycopg.connect(DB_URL, autocommit=True, row_factory=dict_row)  # type: ignore[name-defined]
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with closing(get_conn()) as conn:
        if USE_POSTGRES:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS todos (id TEXT PRIMARY KEY, title TEXT, done BOOLEAN)"
            )
        else:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS todos (id TEXT PRIMARY KEY, title TEXT, done INTEGER)"
            )
        conn.commit() if hasattr(conn, "commit") else None  # psycopg autocommit, sqlite needs commit

def all_todos() -> Dict[str, Dict[str, str]]:
    with closing(get_conn()) as conn:
        rows = conn.execute("SELECT id, title, done FROM todos").fetchall()
        # rows are dict-like for both backends
        return {row["id"]: {"title": row["title"], "done": bool(row["done"]) } for row in rows}

def add_todo(title: str) -> str:
    todo_id = str(uuid.uuid4())
    with closing(get_conn()) as conn:
        if USE_POSTGRES:
            conn.execute(
                "INSERT INTO todos (id, title, done) VALUES (%s, %s, %s)",
                (todo_id, title, False),
            )
        else:
            conn.execute(
                "INSERT INTO todos (id, title, done) VALUES (?, ?, ?)",
                (todo_id, title, 0),
            )
        conn.commit() if hasattr(conn, "commit") else None
    return todo_id

def mark_done(todo_id: str):
    with closing(get_conn()) as conn:
        if USE_POSTGRES:
            conn.execute("UPDATE todos SET done = TRUE WHERE id = %s", (todo_id,))
        else:
            conn.execute("UPDATE todos SET done = 1 WHERE id = ?", (todo_id,))
        conn.commit() if hasattr(conn, "commit") else None

init_db()
app = FastAPI(title="Todo API")

class TodoIn(BaseModel):
    title: str

@app.get("/health")
def healthcheck():
    return {"status": "ok"}

@app.get("/todos")
def list_todos():
    return all_todos()

@app.post("/todos")
def create(todo: TodoIn):
    todo_id = add_todo(todo.title)
    return {"id": todo_id, "title": todo.title, "done": False}

@app.post("/todos/{todo_id}/done")
def complete(todo_id: str):
    mark_done(todo_id)
    return {"id": todo_id, "done": True}