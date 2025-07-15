import requests
import time
import uuid
import os
import json

BASE_URL = "https://ai-remote-backend-production.up.railway.app/api/agent"
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
            print("Polling for task...")
            response = requests.get(f"{BASE_URL}/task/{agent_id}")
            if response.status_code == 200:
                data = response.json()
                command = data.get("command")
                if command:
                    print(f"Received command: {command}")
                    output = os.popen(command).read()

                    result_payload = {
                        "task_id": data["task_id"],
                        "output": output
                    }

                    print(f"Sending result for task {data['task_id']}")
                    res = requests.post(f"{BASE_URL}/result", json=result_payload)
                    print(f"Result sent. Status: {res.status_code}")
                else:
                    print("No command received.")
            else:
                print(f"No task. Server responded: {response.status_code}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        time.sleep(5)

# Register the agent
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
