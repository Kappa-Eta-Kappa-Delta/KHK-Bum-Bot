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
    flow.redirect_uri = "http://localhost"
    auth_url, _ = flow.authorization_url(prompt="consent")
    print("Open this URL in your browser:\n")
    print(auth_url)
    print("\nAfter clicking Allow, your browser will show an error page (that's fine).")
    print("Copy the full URL from the address bar and paste it here.")
    redirect = input("\nPaste the full redirect URL: ").strip()
    from urllib.parse import urlparse, parse_qs
    code = parse_qs(urlparse(redirect).query)["code"][0]
    flow.fetch_token(code=code)
    Path("token.json").write_text(flow.credentials.to_json())
    print("token.json saved.")


if __name__ == "__main__":
    main()
