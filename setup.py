"""
To get your own Obsidian sync server going, simply run this python script and it
will guide you through the process.

It starts by making the directory structure required for docker compose. Then,
it will prompt you for your tailscale auth key. If you don't know how to create
a tailscale auth key, then refer to the readme for a quick guide.

The script will also generate a password for CouchDB and store everything in a
.env file. At the end it prints the CouchDB username and password, which you will
need when setting up the Self-hosted LiveSync plugin in Obsidian.
"""

from getpass import getpass
from pathlib import Path
from secrets import token_urlsafe
import os
import re
import sys

# Make sure that no matter where the script is being ran from, it always works relative
# to the parent directory of where the script lives
project_dir = Path(__file__).resolve().parent

# These are directories that are needed for the compose file and are NOT tracked by git
directories = [
    "tailscale/state",
    "couchdb/data",
]
for directory in directories:
    (project_dir / directory).mkdir(parents=True, exist_ok=True)

# CouchDB runs as uid/gid 5984 inside the container. You normally don't need to do anything
# about that: the container starts as root and chowns its data directory on every start.
# If this script happens to be run as root on Linux, we hand the directory over right away.
COUCHDB_UID = 5984
if hasattr(os, "geteuid") and os.geteuid() == 0:
    os.chown(project_dir / "couchdb" / "data", COUCHDB_UID, COUCHDB_UID)


ts_auth_key = getpass("Paste your tailscale auth key: ").strip()
if not ts_auth_key:
    print("Auth key must not be of length zero!")
    sys.exit(1)
project_name = input("Project name (for docker compose): ").strip() # Project names are important if you host more than one instance
if not project_name:
    print("You must provide a project name!")
    sys.exit(1)
# Docker compose only accepts lowercase letters, numbers, dashes and underscores
if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", project_name):
    print("Project name may only contain lowercase letters, numbers, dashes and underscores!")
    sys.exit(1)
ts_hostname = input("Tailscale hostname (blank for default of obsidian): ").strip()
if not ts_hostname:
    ts_hostname = "obsidian"
couchdb_user = input("CouchDB username (blank for default of obsidian): ").strip()
if not couchdb_user:
    couchdb_user = "obsidian"
# The CouchDB container won't start unless the admin name begins with two letters/numbers
if not re.fullmatch(r"\w{2}[\w-]*", couchdb_user):
    print("CouchDB username must start with 2 letters or numbers, and only contain letters, numbers, - and _!")
    sys.exit(1)

# token_urlsafe only uses letters, numbers, - and _, so it is safe in .env and in URLs
couchdb_password = token_urlsafe(24)


env_contents = (
    f"TS_AUTHKEY={ts_auth_key}\n"
    f"TS_HOSTNAME={ts_hostname}\n"
    f"PROJECT_NAME={project_name}\n"
    f"COUCHDB_USER={couchdb_user}\n"
    f"COUCHDB_PASSWORD={couchdb_password}\n"
)
env_file = project_dir / ".env"
if env_file.exists():
    print("Env file already exists! It was left unchanged.")
    sys.exit(1)
with env_file.open('x', encoding="utf-8") as f:
    f.write(env_contents)


print()
print("Setup complete! You will need these for the Self-hosted LiveSync plugin:")
print(f"  CouchDB username: {couchdb_user}")
print(f"  CouchDB password: {couchdb_password}")
print("They are also stored in your .env file if you ever need them again.")
print()
print("Now start the stack with:")
print("  docker compose up -d")
print(f"Your server will be available at https://{ts_hostname}.<your tailnet>.ts.net")
