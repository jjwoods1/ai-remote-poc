import os
import time
import uuid
import requests
import subprocess
import ast
import json
from redis import Redis

BASE_URL = "https://ai-remote-backend-production.up.railway.app/api/agent"
REDIS_URL = os.getenv("REDISHOST", "redis://localhost:6379")
AGENT_ID_FILE = "agent_id.txt"

# Get or create persistent agent ID
if os.path.exists(AGENT_ID_FILE):
    with open(AGENT_ID_FILE, "r") as f:
        agent_id = f.read().strip()
else:
    agent_id = str(uuid.uuid4())
    with open(AGENT_ID_FILE, "w") as f:
        f.write(agent_id)

print(f"Agent ID: {agent_id}")

# Connect to Redis
r = Redis.from_url(REDIS_URL, decode_responses=True)

# Register agent
try:
    res = requests.post(BASE_URL + "/register", json={"agent_id": agent_id})
    if res.status_code == 200:
        print("Registered with backend.")
    else:
        print("Failed to register:", res.text)
except Exception as e:
    print("Registration error:", e)

print("Agent started. Polling for tasks...")

while True:
    try:
        task_raw = r.lpop(f"queue:{agent_id}")
        if task_raw:
            try:
                task = ast.literal_eval(task_raw)
                task_id = task.get("task_id")
                command = task.get("command")
                print(f"Received task: {task}")

                try:
                    output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=15)
                    output_text = output.decode().strip()
                except subprocess.CalledProcessError as e:
                    output_text = f"[Error] {e.output.decode().strip()}"
                except Exception as e:
                    output_text = f"[Exception] {str(e)}"

                r.set(f"result:{task_id}", output_text, ex=60)
                print(f"Sent result for task {task_id}")
            except Exception as e:
                print(f"Error parsing task: {e}")
        time.sleep(5)
    except Exception as e:
        print(f"Unexpected error: {e}")
        time.sleep(5)
