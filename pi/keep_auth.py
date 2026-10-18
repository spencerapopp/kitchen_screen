#!/usr/bin/env python3
"""One-time Google Keep sign-in for the kitchen screen.

Use a DEDICATED Google account (e.g. a new poppboard.kitchen@gmail.com), not your main
one: the token saved here can read that whole account. Share only the notes the screen
should show (Family List, Olivia's quotes) with it from Keep.

1. In a private browser window, sign in to the dedicated account at
       https://accounts.google.com/EmbeddedSetup
   and click "I agree" (the page may keep spinning; that's fine).
2. Press F12 > Application (Chrome) or Storage (Firefox) > Cookies > accounts.google.com,
   and copy the value of "oauth_token" (starts with oauth2_4/). It works once, for a few minutes.
3. On the Pi:
       ~/kitchen_screen/pi/.venv/bin/python ~/kitchen_screen/pi/keep_auth.py
"""
import json
import os
import secrets
import sys

CONF = os.path.expanduser("~/.config/kitchen/config.json")


def main():
    try:
        import gkeepapi
        import gpsoauth
    except ImportError:
        sys.exit("Install first:  ~/kitchen_screen/pi/.venv/bin/pip install gkeepapi")
    print(__doc__)
    email = input("Dedicated Google account email: ").strip()
    oauth = input("oauth_token cookie value: ").strip()
    res = gpsoauth.exchange_token(email, oauth, secrets.token_hex(8))
    master = res.get("Token", "")
    if not master.startswith("aas_et/"):
        sys.exit(f"Google didn't accept that token ({res.get('Error', 'no master token returned')}). "
                 "Get a fresh oauth_token and run this again right away.")

    keep = gkeepapi.Keep()
    keep.authenticate(email, master, sync=True)
    titles = sorted({(n.title or "").strip() for n in keep.all() if not n.trashed and (n.title or "").strip()})
    print("\nNotes this account can see:", ", ".join(titles) or "(none yet: share your notes with it)")

    cfg = json.load(open(CONF)) if os.path.exists(CONF) else {}
    old = cfg.get("keep") or {}
    fam = input(f"Family list note title [{old.get('family_list', 'Family List')}]: ").strip() or old.get("family_list", "Family List")
    quo = input(f"Olivia quotes note title [{old.get('quotes_note', 'Olivia')}]: ").strip() or old.get("quotes_note", "Olivia")
    cfg["keep"] = {"email": email, "master_token": master, "family_list": fam, "quotes_note": quo}
    with open(CONF, "w") as f:
        json.dump(cfg, f, indent=2)
    os.chmod(CONF, 0o600)
    for t in (fam, quo):
        hit = any(t.lower() in x.lower() for x in titles)
        print(f"  {'found' if hit else 'NOT FOUND (share it with ' + email + ')'}: {t}")
    print("\nSaved. Restart the screen's server:  systemctl --user restart kitchen")


if __name__ == "__main__":
    main()
