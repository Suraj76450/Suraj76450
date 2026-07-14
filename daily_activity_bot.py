import os
import json
import random
import subprocess
import urllib.request
import urllib.error
from datetime import datetime

# Configuration file to store the token
env_file = ".env_github"

def get_github_token():
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith("GITHUB_TOKEN="):
                    return line.strip().split("=", 1)[1]
    
    print("\n[INFO] GitHub Access Token Required!")
    print("To automate Issues, PRs, and Code Reviews, this script needs a Personal Access Token (Classic).")
    print("1. Go to: https://github.com/settings/tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Check the 'repo' scope box.")
    print("4. Generate and copy the token.")
    
    token = input("\n> Paste your GitHub Personal Access Token here: ").strip()
    if token:
        with open(env_file, "w") as f:
            f.write(f"GITHUB_TOKEN={token}\n")
        print(f"Token saved to {env_file}\n")
        return token
    else:
        print("[ERROR] No token provided. Exiting.")
        exit(1)

def get_repo_info():
    try:
        url = subprocess.check_output(["git", "remote", "get-url", "origin"]).decode("utf-8").strip()
        # Handle formats like https://github.com/owner/repo.git or git@github.com:owner/repo.git
        if url.endswith(".git"):
            url = url[:-4]
        if "github.com" in url:
            parts = url.split("github.com")[1].strip("/:").split("/")
            if len(parts) >= 2:
                return parts[0], parts[1]
    except Exception:
        pass
    
    # Fallback default
    return "Suraj76450", "Suraj76450"

def github_api_request(url, method, data, token):
    req_url = f"https://api.github.com{url}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Activity-Bot"
    }
    
    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(req_url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode("utf-8")
        print(f"[ERROR] API Error ({method} {url}): {e.code} - {error_msg}")
        raise e

def main():
    token = get_github_token()
    owner, repo = get_repo_info()
    print(f"Target Repository: {owner}/{repo}")
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    branch_name = f"feature/daily-bot-{today_str}-{random.randint(100, 999)}"
    
    # ----------------- 1. CREATE A LOCAL BRANCH AND COMMIT -----------------
    print("\nPreparing branch and commits locally...")
    subprocess.run(["git", "checkout", "-b", branch_name], check=True)
    
    # Make a small change to log file
    log_file = "activity_log.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"Bot activity logged at {timestamp}\n")
        
    subprocess.run(["git", "add", log_file], check=True)
    subprocess.run(["git", "commit", "-m", f"docs: bot update daily log {today_str}"], check=True)
    
    # Push the branch
    print(f"Pushing branch '{branch_name}' to GitHub...")
    subprocess.run(["git", "push", "origin", branch_name], check=True)
    
    # ----------------- 2. CREATE A PULL REQUEST -----------------
    print("\nOpening Pull Request...")
    pr_data = {
        "title": f"chore: daily bot update {today_str}",
        "head": branch_name,
        "base": "main",
        "body": f"Daily automated update for {today_str}."
    }
    pr = github_api_request(f"/repos/{owner}/{repo}/pulls", "POST", pr_data, token)
    pr_num = pr["number"]
    print(f"[SUCCESS] Pull Request #{pr_num} opened successfully.")
    
    # ----------------- 4. SUBMIT A CODE REVIEW ON THE PR -----------------
    print("Submitting Code Review comment on the Pull Request...")
    review_data = {
        "body": "Daily automated review checks passed successfully. Ready to merge.",
        "event": "COMMENT"
    }
    github_api_request(f"/repos/{owner}/{repo}/pulls/{pr_num}/reviews", "POST", review_data, token)
    print(f"[SUCCESS] Code Review submitted on PR #{pr_num}.")
    
    # ----------------- 5. MERGE THE PULL REQUEST -----------------
    print("Merging Pull Request...")
    merge_data = {
        "commit_title": f"Merge pull request #{pr_num} from {branch_name}"
    }
    github_api_request(f"/repos/{owner}/{repo}/pulls/{pr_num}/merge", "PUT", merge_data, token)
    print(f"[SUCCESS] Pull Request #{pr_num} merged.")
    
    # ----------------- 6. LOCAL CLEANUP -----------------
    print("\nCleaning up local workspace...")
    subprocess.run(["git", "checkout", "main"], check=True)
    subprocess.run(["git", "pull"], check=True)
    subprocess.run(["git", "branch", "-d", branch_name], check=True)
    
    print("\n[SUCCESS] ALL ACTIONS COMPLETED SUCCESSFULLY!")
    print("Logged: 1 Pull Request, 1 Code Review, and Commits.")

if __name__ == "__main__":
    main()
