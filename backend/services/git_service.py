import os
import re
import uuid
from git import Repo

# ✅ Clone inside D drive instead of system temp
BASE_CLONE_DIR = "D:/temp_clones"


# 2️⃣ Sanitize branch name
def sanitize_branch_name(team_name, leader_name):
    team = re.sub(r"[^A-Z0-9_]", "", str(team_name).upper().replace(" ", "_"))
    leader = re.sub(r"[^A-Z0-9_]", "", str(leader_name).upper().replace(" ", "_"))
    return f"{team}_{leader}_AI_Fix"


# 3️⃣ Clone repository (UPDATED)
def clone_repository(repo_url):

    # Create base clone folder in D drive if not exists
    if not os.path.exists(BASE_CLONE_DIR):
        os.makedirs(BASE_CLONE_DIR)

    # Create unique folder
    folder_name = str(uuid.uuid4())
    clone_path = os.path.join(BASE_CLONE_DIR, folder_name)

    # Clone repo
    repo = Repo.clone_from(repo_url, clone_path)

    return repo, clone_path


# 4️⃣ Create new branch
def create_branch(repo, branch_name):
    if branch_name in repo.heads:
        repo.git.checkout(branch_name)
    else:
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()

    return branch_name


# 5️⃣ Commit changes
def commit_changes(repo, message):
    repo.git.add(all=True)
    if not repo.is_dirty(index=True, working_tree=True, untracked_files=True):
        return False
    full_message = f"[AI-AGENT] {message}"
    repo.index.commit(full_message)
    return True


# 6️⃣ Push branch to GitHub
def push_branch(repo, branch_name):
    origin = repo.remote(name='origin')
    origin.push(refspec=f"{branch_name}:{branch_name}")
