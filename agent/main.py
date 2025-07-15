import requests
import time
import uuid
import os
import json

# The backend URL
BASE_URL = "https://ai-remote-backend-production.up.railway.app/api/agent"

# Persistent agent ID
AGENT_ID_FILE = "agent_id.txt"
if os.path.exists(AGENT_ID_FILE):
    with open(AGENT_ID_FILE, "r") as f:
        agent_id = f.read().strip()
else:
    agent_id = str(uuid.uuid4())
    with open(AGENT_ID_FILE, "w") as f:
        f.write(agent_id)

print(f"Agent ID: {agent_id}")

def poll():
    while True:
        try:
            # Poll for task
            response = requests.get(f"{BASE_URL}/task/{agent_id}")
            if response.status_code == 200 and response.json().get("command"):
                command = response.json()["command"]
                print(f"Received command: {command}")
                output = os.popen(command).read()
                
                result_payload = {
                    "task_id": response.json()["task_id"],
                    "output": output
                }
                requests.post(f"{BASE_URL}/result", json=result_payload)
        except Exception as e:
            print(f"Unexpected error: {e}")

        time.sleep(5)

# Register with backend
try:
    response = requests.post(f"{BASE_URL}/register", json={"agent_id": agent_id})
    if response.status_code == 200:
        print("Registered with backend.")
    else:
        print(f"Failed to register: {response.text}")
except Exception as e:
    print(f"Registration error: {e}")

print("Agent started. Polling for tasks...")
poll()
