import os
import subprocess
import uuid


def create_dockerfile(repo_path):
    dockerfile_content = """
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["pytest"]
"""
    dockerfile_path = os.path.join(repo_path, "Dockerfile")

    if not os.path.exists(dockerfile_path):
        with open(dockerfile_path, "w", encoding="utf-8") as f:
            f.write(dockerfile_content)


def _docker_available():
    probe = subprocess.run(
        ["docker", "info"],
        capture_output=True,
        text=True,
        check=False,
    )
    return probe.returncode == 0, probe.stdout, probe.stderr


def run_tests_in_docker(repo_path):
    image_name = f"test-runner-{uuid.uuid4().hex[:6]}"
    available, _, probe_stderr = _docker_available()
    if not available:
        return {
            "status": "docker_unavailable",
            "stdout": "",
            "stderr": probe_stderr,
            "exit_code": 1,
        }

    create_dockerfile(repo_path)

    build_process = subprocess.run(
        ["docker", "build", "-t", image_name, repo_path],
        capture_output=True,
        text=True,
        check=False,
    )

    if build_process.returncode != 0:
        return {
            "status": "build_failed",
            "stdout": build_process.stdout,
            "stderr": build_process.stderr,
            "exit_code": build_process.returncode
        }

    run_process = subprocess.run(
        ["docker", "run", "--rm", image_name],
        capture_output=True,
        text=True,
        check=False,
    )

    stdout = run_process.stdout
    stderr = run_process.stderr

    if run_process.returncode == 0:
        return {
            "status": "success",
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": 0
        }

    return {
        "status": "failed",
        "exit_code": run_process.returncode,
        "stdout": stdout,
        "stderr": stderr
    }
