
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import uvicorn

from datetime import datetime

import time
import database
import ai_code
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskCreate(BaseModel):
    title: str
    subject: str = ""
    deadline: str = ""
    for_user_id: int
    from_user_id: int

class TaskUpdate(BaseModel):
    done: bool

@app.post("/api/tasks")
async def create_task(task: TaskCreate):
    query = (
            "INSERT INTO tasks (foruser_id, fromuser_id, task_start, task_end, graded) "
            "VALUES (?, ?, ?, ?, ?)"
        )
    print(f"date: {task.deadline}")
    id = await database.db.awrite(query, (task.for_user_id, task.from_user_id, int(time.time()) , ai_code.date_to_seconds(task.deadline), 0))
    tsk =  open(f"tasks/{id}" , "w")
    tsk.write(task.title+"\n"+task.subject)
    tsk.close()
    # conn = sqlite3.connect(DB_PATH)
    # c = conn.cursor()
    # c.execute("INSERT INTO tasks (title, subject, deadline, foruser_id, fromuser_id) VALUES (?,?,?,?,?)",
    #           (task.title, task.subject, task.deadline, task.for_user_id, task.from_user_id))
    # task_id = c.lastrowid
    # conn.commit()
    # conn.close()
    print("[+]site log", str({"success": True, "task_id": id}))
    return {"success": True, "task_id": id}

@app.get("/api/tasks")
async def get_tasks(user_id: int):
    # conn = sqlite3.connect(DB_PATH)
    # c = conn.cursor()
    # c.execute("SELECT id, title, subject, deadline, done FROM tasks WHERE foruser_id = ?", (user_id,))
    # rows = c.fetchall()
    # conn.close()
    tasks = []
    tasks_now = await database.db.aread(
            f"SELECT rowid, * FROM tasks WHERE foruser_id = {user_id} AND task_end > {int(time.time())}"
            )
    
    for r in tasks_now:
        try:
                with open(f"tasks/{r[0]}", "r", encoding="utf-8") as f:
                        task_desc = f.read()
        except FileNotFoundError:
                    task_desc = "Описание отсутствует"
        title = task_desc.split('\n')[0]
        tasks.append({
            "id": r[0], "title": title , "subject": task_desc[len(title): ],
            "deadline": datetime.fromtimestamp(r[5]).strftime('%d.%m.%Y %H:%M'), "done": bool(r[6])
        })
    print("[+]site log", str(tasks))

    return tasks

@app.put("/api/tasks/{task_id}")
async def update_task(task_id: int, update: TaskUpdate):
    # conn = sqlite3.connect(DB_PATH)
    # c = conn.cursor()
    # c.execute("UPDATE tasks SET done = ? WHERE id = ?", (1 if update.done else 0, task_id))
    # conn.commit()
    # conn.close()
    await database.db.awrite(f"UPDATE tasks SET graded = {1 if update.done else 0}  WHERE id = {task_id}")
    print("[+]site log", str({"success": True}))

    return {"success": True}

@app.get("/api/progress")
async def get_progress(user_id: int):
    # conn = sqlite3.connect(DB_PATH)
   
    # c = conn.cursor()
    total, completed = await database.db.aread(f"SELECT COUNT(*), SUM(graded) FROM tasks WHERE foruser_id = {user_id}")
    print("[+]site log", str({"total": total, "completed": completed or 0, "percent": round((completed or 0)*100/total if total else 0)}))

    return {"total": total, "completed": completed or 0, "percent": round((completed or 0)*100/total if total else 0)}

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)