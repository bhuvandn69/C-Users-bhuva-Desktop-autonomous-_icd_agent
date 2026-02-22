from fastapi import FastAPI
from pydantic import BaseModel
import json
import os

from agents.iteration_controller import run_iteration

app = FastAPI()


class RunAgentRequest(BaseModel):
    repo_url: str
    team_name: str
    leader_name: str


@app.post("/run-agent")
def run_agent(data: RunAgentRequest):
    result = run_iteration(
        data.repo_url,
        data.team_name,
        data.leader_name
    )

    # Save results.json
    results_path = os.path.join(os.path.dirname(__file__), "results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

    return result
