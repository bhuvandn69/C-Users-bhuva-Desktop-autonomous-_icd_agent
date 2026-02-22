import time
import os

from classifier import parse_failure
from docker_runner import run_tests_in_docker
from fixer import apply_fix
from services.scoring import calculate_score
from services.git_service import (
    clone_repository,
    sanitize_branch_name,
    create_branch,
    commit_changes,
    push_branch
)


def run_iteration(repo_url, team_name, leader_name):
    start_time = time.time()
    repo, clone_path = clone_repository(repo_url)
    branch_name = sanitize_branch_name(team_name, leader_name)
    create_branch(repo, branch_name)
    push_branch(repo, branch_name)

    max_retries = int(os.getenv("MAX_RETRIES", "5"))
    fixes = []
    total_failures = 0
    fixes_applied = 0
    commits = 0
    iterations = 0
    ci_status = "FAILED"
    last_test_result = None

    for i in range(max_retries):
        iterations = i + 1
        test_result = run_tests_in_docker(clone_path)
        last_test_result = test_result
        status = test_result.get("status")

        if status == "success":
            ci_status = "PASSED"
            break

        if status in ("docker_unavailable", "build_failed"):
            ci_status = "ERROR"
            break

        combined_logs = f"{test_result.get('stdout', '')}\n{test_result.get('stderr', '')}"
        failure_details = parse_failure(combined_logs)
        total_failures += 1

        fixed = apply_fix(clone_path, failure_details)
        bug_type = failure_details.get("bug_type", "UNKNOWN")
        commit_message = f"Fix {bug_type} issue"

        if fixed:
            fixes_applied += 1
            committed = commit_changes(repo, commit_message)
            if committed:
                commits += 1
                push_branch(repo, branch_name)
            fix_status = "Fixed"
        else:
            fix_status = "Failed"

        fixes.append({
            "file": failure_details.get("file"),
            "bug_type": bug_type,
            "line": failure_details.get("line"),
            "commit_message": f"[AI-AGENT] {commit_message}",
            "status": fix_status,
        })

        if not fixed:
            break

    end_time = time.time()
    total_time = round(end_time - start_time, 2)
    score = calculate_score(total_time_seconds=total_time, commits=commits)

    return {
        "repo_url": repo_url,
        "team_name": team_name,
        "leader_name": leader_name,
        "branch_name": branch_name,
        "total_failures": total_failures,
        "fixes_applied": fixes_applied,
        "iterations": iterations,
        "ci_status": ci_status,
        "commits": commits,
        "score": score,
        "fixes": fixes,
        "clone_path": clone_path,
        "time_taken": total_time,
        "test_result": last_test_result,
    }
