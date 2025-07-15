import requests
import time
import uuid
import os
import subprocess
import json

# Your deployed backend's agent endpoint
BASE_URL = "https://ai-remote-backend-production.up.railway.app/api/agent"

# Generate or load agent ID (this ensures a persistent unique ID)
AGENT_ID_FILE = "agent_id.txt"
if os.path.exists(AGENT_ID_FILE):
    with open(AGENT_ID_FILE, "r") as f:
        AGENT_ID = f.read().strip()
else:
    AGENT_ID = str(uuid.uuid4())
    with open(AGENT_ID_FILE, "w") as f:
        f.write(AGENT_ID)

print(f"Agent ID: {AGENT_ID}")

def register():
    try:
        res = requests.post(f"{BASE_URL}/register", json={"agent_id": AGENT_ID})
        if res.status_code == 200:
            print("Registered with backend.")
        else:
            print("Failed to register:", res.text)
    except Exception as e:
        print(f"Registration error: {e}")

def poll_for_commands():
    try:
        res = requests.get(f"{BASE_URL}/poll/{AGENT_ID}")
        if res.status_code == 200:
            task = res.json()
            if task and "task_id" in task and "command" in task:
                print(f"Executing command: {task['command']}")
                output = run_command(task["command"])
                submit_result(task["task_id"], output)
    except Exception as e:
        print(f"Polling error: {e}")

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)

def submit_result(task_id, output):
    try:
        res = requests.post(f"{BASE_URL}/result", json={
            "task_id": task_id,
            "output": output
        })
        if res.status_code == 200:
            print("Result submitted.")
        else:
            print("Failed to submit result:", res.text)
    except Exception as e:
        print(f"Submit error: {e}")

# === Main Loop ===
if __name__ == "__main__":
    print("Agent started. Polling for tasks...")
    register()
    while True:
        poll_for_commands()
        time.sleep(5)
