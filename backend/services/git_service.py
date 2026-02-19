import os
import re
import random
import string
from git import Repo

# Clone inside system /tmp directory
BASE_CLONE_DIR = "/tmp"


# 1️⃣ Generate random folder name
def generate_random_folder():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))


# 2️⃣ Sanitize branch name
def sanitize_branch_name(team_name, leader_name):
    # Combine names
    branch = f"{team_name}_{leader_name}_AI_Fix"

    # Convert to uppercase
    branch = branch.upper()

    # Replace spaces with underscore
    branch = branch.replace(" ", "_")

    # Remove special characters
    branch = re.sub(r'[^A-Z0-9_]', '', branch)

    # Ensure it ends EXACTLY with _AI_FIX
    if not branch.endswith("_AI_FIX"):
        branch = branch + "_AI_FIX"

    return branch


# 3️⃣ Clone repository
def clone_repository(repo_url):
    if not os.path.exists(BASE_CLONE_DIR):
        os.makedirs(BASE_CLONE_DIR)

    folder_name = generate_random_folder()
    clone_path = os.path.join(BASE_CLONE_DIR, folder_name)

    repo = Repo.clone_from(repo_url, clone_path)

    return repo, clone_path


# 4️⃣ Create new branch
def create_branch(repo, branch_name):
    # Check if branch already exists
    if branch_name in repo.heads:
        repo.git.checkout(branch_name)
    else:
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()

    return branch_name


# 5️⃣ Commit changes
def commit_changes(repo, message):
    repo.git.add(all=True)

    # Ensure commit starts with required prefix
    full_message = f"[AI-AGENT] {message}"

    repo.index.commit(full_message)


# 6️⃣ Push branch to GitHub
def push_branch(repo, branch_name):
    origin = repo.remote(name='origin')

    # Push ONLY the new branch
    origin.push(refspec=f"{branch_name}:{branch_name}")
