import os
import json
import hashlib
import shutil
from datetime import datetime

class MiniGit:
    def __init__(self):
        self.repo_dir = os.getcwd()
        self.minigit_dir = os.path.join(self.repo_dir, '.minigit')
        self.commits_dir = os.path.join(self.minigit_dir, 'commits')
        self.staging_file = os.path.join(self.minigit_dir, 'staging.json')
        self.head_file = os.path.join(self.minigit_dir, 'HEAD')

    def init(self):
        if os.path.exists(self.minigit_dir):
            print("Repository already initialized")
            return
        
        os.makedirs(self.commits_dir)
        with open(self.staging_file, 'w') as f:
            json.dump({}, f)
        with open(self.head_file, 'w') as f:
            f.write("")
        
        print("Initialized empty Mini Git repository")

    def add(self, filename):
        if not os.path.exists(self.minigit_dir):
            print("Not a minigit repository. Run 'init' first")
            return
        
        if not os.path.exists(filename):
            print(f"File '{filename}' not found")
            return
        
        with open(filename, 'r') as f:
            content = f.read()
        
        with open(self.staging_file, 'r') as f:
            staging = json.load(f)
        
        staging[filename] = content
        
        with open(self.staging_file, 'w') as f:
            json.dump(staging, f, indent=2)
        
        print(f"Added '{filename}' to staging area")

    def commit(self, message):
        if not os.path.exists(self.minigit_dir):
            print("Not a minigit repository. Run 'init' first")
            return
        
        with open(self.staging_file, 'r') as f:
            staging = json.load(f)
        
        if not staging:
            print("Nothing to commit. Use 'add' to stage files")
            return
        
        commit_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:10]
        
        commit_data = {
            'id': commit_id,
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'files': staging
        }
        
        commit_file = os.path.join(self.commits_dir, f"{commit_id}.json")
        with open(commit_file, 'w') as f:
            json.dump(commit_data, f, indent=2)
        
        with open(self.head_file, 'w') as f:
            f.write(commit_id)
        
        with open(self.staging_file, 'w') as f:
            json.dump({}, f)
        
        print(f"Committed: [{commit_id}] {message}")

    def log(self):
        if not os.path.exists(self.minigit_dir):
            print("Not a minigit repository. Run 'init' first")
            return
        
        commits = []
        for filename in os.listdir(self.commits_dir):
            if filename.endswith('.json'):
                with open(os.path.join(self.commits_dir, filename), 'r') as f:
                    commits.append(json.load(f))
        
        if not commits:
            print("No commits yet")
            return
        
        commits.sort(key=lambda x: x['timestamp'], reverse=True)
        
        print("\n=== Commit History ===")
        for commit in commits:
            print(f"\nCommit: {commit['id']}")
            print(f"Date: {commit['timestamp']}")
            print(f"Message: {commit['message']}")
            print(f"Files: {', '.join(commit['files'].keys())}")

    def status(self):
        if not os.path.exists(self.minigit_dir):
            print("Not a minigit repository. Run 'init' first")
            return
        
        with open(self.staging_file, 'r') as f:
            staging = json.load(f)
        
        print("\n=== Repository Status ===")
        if staging:
            print("Staged files:")
            for filename in staging:
                print(f"  - {filename}")
        else:
            print("No files staged")

    def checkout(self, commit_id):
        if not os.path.exists(self.minigit_dir):
            print("Not a minigit repository. Run 'init' first")
            return
        
        commit_file = os.path.join(self.commits_dir, f"{commit_id}.json")
        if not os.path.exists(commit_file):
            print(f"Commit '{commit_id}' not found")
            return
        
        with open(commit_file, 'r') as f:
            commit_data = json.load(f)
        
        for filename, content in commit_data['files'].items():
            with open(filename, 'w') as f:
                f.write(content)
        
        with open(self.head_file, 'w') as f:
            f.write(commit_id)
        
        print(f"Checked out commit: {commit_id}")
        print(f"Restored {len(commit_data['files'])} file(s)")

    def diff(self):
        if not os.path.exists(self.minigit_dir):
            print("Not a minigit repository. Run 'init' first")
            return
        
        with open(self.head_file, 'r') as f:
            head = f.read().strip()
        
        if not head:
            print("No commits yet")
            return
        
        commit_file = os.path.join(self.commits_dir, f"{head}.json")
        with open(commit_file, 'r') as f:
            commit_data = json.load(f)
        
        print("\n=== Changes ===")
        changes_found = False
        
        for filename in commit_data['files']:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    current = f.read()
                
                if current != commit_data['files'][filename]:
                    print(f"\nModified: {filename}")
                    changes_found = True
        
        if not changes_found:
            print("No changes detected")

def main():
    git = MiniGit()
    
    print("=== Mini Git ===")
    print("Commands: init, add <file>, commit <message>, log, status, checkout <id>, diff, exit\n")
    
    while True:
        command = input("minigit> ").strip().split(maxsplit=1)
        
        if not command:
            continue
        
        cmd = command[0]
        
        if cmd == "init":
            git.init()
        
        elif cmd == "add":
            if len(command) < 2:
                print("Usage: add <filename>")
            else:
                git.add(command[1])
        
        elif cmd == "commit":
            if len(command) < 2:
                print("Usage: commit <message>")
            else:
                git.commit(command[1])
        
        elif cmd == "log":
            git.log()
        
        elif cmd == "status":
            git.status()
        
        elif cmd == "checkout":
            if len(command) < 2:
                print("Usage: checkout <commit_id>")
            else:
                git.checkout(command[1])
        
        elif cmd == "diff":
            git.diff()
        
        elif cmd == "exit":
            break
        
        else:
            print("Unknown command")

if __name__ == "__main__":
    main()
