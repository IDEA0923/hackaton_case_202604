from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "/data/database.db"

class TaskCreate(BaseModel):
    title: str
    subject: str = ""
    deadline: str = ""
    for_user_id: int
    from_user_id: int

class TaskUpdate(BaseModel):
    done: bool

@app.post("/api/tasks")
def create_task(task: TaskCreate):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO tasks (title, subject, deadline, foruser_id, fromuser_id) VALUES (?,?,?,?,?)",
              (task.title, task.subject, task.deadline, task.for_user_id, task.from_user_id))
    task_id = c.lastrowid
    conn.commit()
    conn.close()
    return {"success": True, "task_id": task_id}

@app.get("/api/tasks")
def get_tasks(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title, subject, deadline, done FROM tasks WHERE foruser_id = ?", (user_id,))
    rows = c.fetchall()
    conn.close()
    tasks = []
    for r in rows:
        tasks.append({
            "id": r[0], "title": r[1], "subject": r[2],
            "deadline": r[3], "done": bool(r[4])
        })
    return tasks

@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, update: TaskUpdate):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE tasks SET done = ? WHERE id = ?", (1 if update.done else 0, task_id))
    conn.commit()
    conn.close()
    return {"success": True}

@app.get("/api/progress")
def get_progress(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(done) FROM tasks WHERE foruser_id = ?", (user_id,))
    total, completed = c.fetchone()
    conn.close()
    return {"total": total, "completed": completed or 0, "percent": round((completed or 0)*100/total if total else 0)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)