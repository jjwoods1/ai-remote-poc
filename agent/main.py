# agent/main.py
import time
import subprocess
import requests

BACKEND_URL = "https://ai-remote-backend-production.up.railway.app/api/agent"

def fetch_task():
    try:
        res = requests.get(f"{BACKEND_URL}/api/task/next", timeout=10)
        return res.json() if res.status_code == 200 else None
    except:
        return None

def submit_result(task_id, result):
    try:
        requests.post(f"{BACKEND_URL}/api/task/{task_id}/result", json={"result": result}, timeout=10)
    except:
        pass

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    print("Agent started. Polling for tasks...")
    while True:
        task = fetch_task()
        if task and "task_id" in task:
            print(f"Running: {task['command']}")
            output = run_command(task["command"])
            submit_result(task["task_id"], output)
        time.sleep(5)

