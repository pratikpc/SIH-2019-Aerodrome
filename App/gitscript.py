import subprocess
import sys
from datetime import datetime

# Get the REPO Location
repo = sys.argv[1]

def RunGit(commands: list):
    # Prepend Git Name
    commands.insert(0,'git') 
    # Pass Required Argument to Python
    completed = subprocess.run(
     commands, # The Python Commands to Run
     cwd=repo, # Set CWD to REPO
     shell=True # Ensure it can access current CMD path
    )
    return completed
RunGit(['init']) # Init REPO
RunGit(['add','-A']) # Stage only Tracked Files
git_message = 'Git Update at ' + str(datetime.now())
RunGit(['commit','-m',git_message]) # Add with Commit Message
RunGit(['push']) # Push Changes
RunGit(['pull']) #Pull any external changes (maybe you deleted a file from your repo?)
