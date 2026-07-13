import os
import random
import subprocess
from datetime import datetime

# Choose a random number of commits between 10 and 12
num_commits = random.randint(10, 12)
log_file = "activity_log.txt"

print(f"Generating {num_commits} daily commits...")

for i in range(1, num_commits + 1):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"Activity logged at {timestamp} - commit {i} of {num_commits}\n"
    
    # 1. Append log entry
    with open(log_file, "a") as f:
        f.write(log_message)
        
    # 2. Stage the file
    subprocess.run(["git", "add", log_file], check=True)
    
    # 3. Commit the change
    commit_msg = f"docs: update daily activity log - entry {i} of {num_commits}"
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
    print(f"Committed: {commit_msg}")

# 4. Push all commits to GitHub
print("Pushing commits to GitHub...")
subprocess.run(["git", "push", "origin", "main"], check=True)
print("Done! All commits have been pushed successfully.")
