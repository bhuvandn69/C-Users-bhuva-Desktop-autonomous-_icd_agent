from fastapi import FastAPI
from pydantic import BaseModel
import time
import json

app = FastAPI()

class RunAgentRequest(BaseModel):
    repo_url: str
    team_name: str
    leader_name: str


@app.post("/run-agent")
def run_agent(data: RunAgentRequest):

    start_time = time.time()

    result = {
        "repo_url": data.repo_url,
        "team_name": data.team_name,
        "leader_name": data.leader_name,
        "ci_status": "STARTED"
    }

    end_time = time.time()
    result["time_taken"] = round(end_time - start_time, 2)

    # 🔥 THIS IS THE IMPORTANT PART
    with open("results.json", "w") as f:
        json.dump(result, f, indent=4)

    return result
