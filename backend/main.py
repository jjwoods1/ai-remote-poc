# backend/main.py
import uuid
import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
import redis

app = FastAPI(title="Remote Command API")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

class CommandRequest(BaseModel):
    command: str

class ResultResponse(BaseModel):
    result: str

@app.post("/api/command")
def queue_command(req: CommandRequest):
    task_id = str(uuid.uuid4())
    r.set(f"task:{task_id}:cmd", req.command)
    return {"task_id": task_id}

@app.get("/api/task/{task_id}")
def get_task_result(task_id: str):
    result = r.get(f"task:{task_id}:result")
    if result:
        return {"status": "complete", "result": result}
    return {"status": "pending"}

@app.get("/api/task/next")
def get_next_task():
    keys = r.keys("task:*:cmd")
    if not keys:
        return {}
    task_key = keys[0]
    task_id = task_key.split(":")[1]
    command = r.get(task_key)
    r.delete(task_key)
    return {"task_id": task_id, "command": command}

@app.post("/api/task/{task_id}/result")
def post_result(task_id: str, res: ResultResponse):
    r.set(f"task:{task_id}:result", res.result)
    return {"status": "ok"}
