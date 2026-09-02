"""
Run this once on any machine with a browser to authorize Google Drive access.
It will save token.json, which the bot uses to upload files.

Usage:
    python setup_drive.py
"""
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def main():
    secret = Path("client_secret.json")
    if not secret.exists():
        sys.exit("client_secret.json not found. Place it in the repo root and try again.")
    flow = InstalledAppFlow.from_client_secrets_file(str(secret), SCOPES)
    creds = flow.run_console()
    Path("token.json").write_text(creds.to_json())
    print("token.json saved.")


if __name__ == "__main__":
    main()
