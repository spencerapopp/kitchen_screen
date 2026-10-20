#!/usr/bin/env python3
"""Set up "Spencer is on his way home" for the kitchen screen.

Your phone's OwnTracks app posts its location to the Pi over Tailscale (a private network
between your own devices). Only the /owntracks address is shared with your devices; the
dashboard itself stays private to the Pi.

Before running this:
  1. Install Tailscale on the Pi:   curl -fsSL https://tailscale.com/install.sh | sh
                                    sudo tailscale up        (open the link it prints, sign in)
  2. Install Tailscale on your phone and sign in with the same account.
Then:   python3 ~/kitchen_screen/pi/eta_setup.py
"""
import json
import os
import secrets
import subprocess
import sys
import urllib.request

CONF = os.path.expanduser("~/.config/kitchen/config.json")
PORT = 8080


def main():
    try:
        st = json.loads(subprocess.run(["tailscale", "status", "--json"], capture_output=True, text=True).stdout)
    except (FileNotFoundError, json.JSONDecodeError):
        sys.exit("Tailscale isn't installed or running yet. See step 1 at the top of this file.")
    host = (st.get("Self") or {}).get("DNSName", "").rstrip(".")
    if st.get("BackendState") != "Running" or not host:
        sys.exit("Tailscale isn't signed in yet. Run:  sudo tailscale up   and open the link it prints.")

    cfg = json.load(open(CONF))
    e = cfg.get("eta") or {}
    mt = cfg.get("morning_trip") or []
    mt = mt if isinstance(mt, list) else [mt]
    me = next((t for t in mt if t.get("name") == "Spencer"), mt[0] if mt else {})
    e.setdefault("name", me.get("name", "Spencer"))
    e.setdefault("work", me.get("to"))
    e.setdefault("token", secrets.token_urlsafe(12))
    if not e.get("work"):
        sys.exit("No work address found in config.json (morning_trip). Add \"work\" under \"eta\".")
    cfg["eta"] = e
    with open(CONF, "w") as f:
        json.dump(cfg, f, indent=2)
    os.chmod(CONF, 0o600)

    print("Sharing /owntracks with your Tailscale devices (needs sudo)...")
    r = subprocess.run(["sudo", "tailscale", "serve", "--bg", "--https=443", "--set-path=/owntracks",
                        f"http://127.0.0.1:{PORT}/owntracks"])
    if r.returncode:
        sys.exit("tailscale serve didn't finish. If it printed a link to enable HTTPS, open it, "
                 "click Enable, then run this again.")

    subprocess.run(["systemctl", "--user", "restart", "kitchen"])
    import time
    time.sleep(3)
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{PORT}/owntracks/{e['token']}", data=b'{"_type":"test"}',
                                     headers={"Content-Type": "application/json"})
        ok = urllib.request.urlopen(req, timeout=10).read() == b"[]"
    except Exception as ex:
        ok = False
        print("Local test failed:", ex)
    print("\nReceiver:", "working" if ok else "NOT answering (check: journalctl --user-unit kitchen -n 40)")
    print("\nIn the OwnTracks app: Preferences > Connection > Mode: HTTP, and set the URL to:\n")
    print(f"    https://{host}/owntracks/{e['token']}\n")
    print("Keep that address private: it's how the screen knows it's really your phone.")


if __name__ == "__main__":
    main()
