#!/usr/bin/env python3
"""One-time Google sign-in for the kitchen dashboard.

Run on the Pi (with the TV showing the desktop):
    ~/kitchen_screen/pi/.venv/bin/python ~/kitchen_screen/pi/google_auth.py CLIENT_ID CLIENT_SECRET

A browser opens; sign in with the Google account that owns the Family list and
the Kitchen Photos folder, and allow read-only access (calendar, tasks, Drive). The Pi stores the result
in ~/.config/kitchen/config.json. Read-only: the dashboard can't change anything.
"""
import json
import os
import secrets
import subprocess
import sys
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

CONFIG = os.path.expanduser("~/.config/kitchen/config.json")
PORT = 8765
SCOPES = ("https://www.googleapis.com/auth/tasks.readonly https://www.googleapis.com/auth/drive.readonly "
          "https://www.googleapis.com/auth/calendar.readonly")


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 1
    client_id, client_secret = sys.argv[1], sys.argv[2]
    redirect = f"http://127.0.0.1:{PORT}/"
    state = secrets.token_urlsafe(16)
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": client_id, "redirect_uri": redirect, "response_type": "code",
        "scope": SCOPES, "access_type": "offline", "prompt": "consent", "state": state})
    got = {}

    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if q.get("state", [""])[0] == state and "code" in q:
                got["code"] = q["code"][0]
                msg = "Done — you can close this tab. The kitchen screen is connected."
            else:
                got["error"] = q.get("error", ["unknown"])[0]
                msg = "Sign-in did not complete: " + got["error"]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"<body style='font:24px sans-serif;padding:40px'>{msg}</body>".encode())

        def log_message(self, *a):
            pass

    srv = HTTPServer(("127.0.0.1", PORT), H)
    print("Opening the Google sign-in page… if nothing opens, visit:\n" + url)
    subprocess.Popen(["chromium-browser" if os.path.exists("/usr/bin/chromium-browser") else "chromium", url],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    while not got:
        srv.handle_request()
    if "code" not in got:
        print("Sign-in failed:", got.get("error"))
        return 1

    body = urllib.parse.urlencode({"code": got["code"], "client_id": client_id, "client_secret": client_secret,
                                   "redirect_uri": redirect, "grant_type": "authorization_code"}).encode()
    tok = json.loads(urllib.request.urlopen("https://oauth2.googleapis.com/token", data=body, timeout=30).read())
    if "refresh_token" not in tok:
        print("Google did not return a refresh token. Remove the app's access at myaccount.google.com/permissions and run this again.")
        return 1

    os.makedirs(os.path.dirname(CONFIG), exist_ok=True)
    cfg = {}
    if os.path.exists(CONFIG):
        with open(CONFIG) as f:
            cfg = json.load(f)
    cfg["google"] = {"client_id": client_id, "client_secret": client_secret, "refresh_token": tok["refresh_token"],
                     "scopes": tok.get("scope", SCOPES)}
    with open(CONFIG, "w") as f:
        json.dump(cfg, f, indent=2)
    os.chmod(CONFIG, 0o600)
    print("Connected. The family list and photos will appear within a couple of minutes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
