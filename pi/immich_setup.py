#!/usr/bin/env python3
"""Connect the kitchen screen's photo panel to Immich (the family photo server on mrpopp).

Before running this, in Immich (http://192.168.4.54:2283), signed in as each person whose
photos should show:
  Account Settings > API Keys > New API Key
  Name: Kitchen screen.  Permissions: asset.read, asset.view, album.read, person.read
Then on the Pi:   python3 ~/kitchen_screen/pi/immich_setup.py
Keys are typed in hidden and saved only in ~/.config/kitchen/config.json on the Pi.
"""
import getpass
import json
import os
import subprocess
import sys
import time
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from immich_source import Immich  # noqa: E402

CONF = os.path.expanduser("~/.config/kitchen/config.json")
DEFAULT_URL = "http://192.168.4.54:2283"


def test(url, key, who):
    api = Immich(url, key, who, timeout=15)
    try:
        api.call("POST", "/search/random", {"size": 1})
    except urllib.error.HTTPError as e:
        return f"key rejected ({e.code}): check it was copied whole and has asset.read" if e.code in (401, 403) \
            else f"Immich answered {e.code}"
    except Exception as e:
        return f"can't reach {url} ({type(e).__name__}). Is mrpopp on and Docker running?"
    for path, perm in (("/albums", "album.read"), ("/people?size=1", "person.read")):
        try:
            api.call("GET", path)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                return f"key works but is missing {perm}"
    return None


def main():
    cfg = json.load(open(CONF)) if os.path.exists(CONF) else {}
    im = cfg.get("immich") or {}
    url = input(f"Immich address [{im.get('url') or DEFAULT_URL}]: ").strip() or im.get("url") or DEFAULT_URL
    keys = dict(im.get("keys") or {})
    if keys:
        print("Already connected:", ", ".join(keys), "(press Enter to keep a key as is)")
    for who in list(keys) or ["Spencer", "Cookie"]:
        k = getpass.getpass(f"API key for {who} (hidden; Enter to {'keep' if who in keys else 'skip'}): ").strip()
        if k:
            keys[who] = k
    while True:
        who = input("Another person's photos? Name, or Enter if done: ").strip()
        if not who:
            break
        k = getpass.getpass(f"API key for {who} (hidden): ").strip()
        if k:
            keys[who] = k
    if not keys:
        sys.exit("No keys entered; nothing changed.")

    bad = {}
    for who, k in keys.items():
        problem = test(url, k, who)
        print(f"  {who}: {'OK' if not problem else problem}")
        if problem:
            bad[who] = problem
    if bad and input("Save anyway? (y/n): ").strip().lower() != "y":
        sys.exit("Nothing saved.")

    im.update(url=url, keys=keys)
    im.setdefault("album", "Kitchen Screen")
    cfg["immich"] = im
    os.makedirs(os.path.dirname(CONF), exist_ok=True)
    with open(CONF + ".tmp", "w") as f:
        json.dump(cfg, f, indent=2)
    os.chmod(CONF + ".tmp", 0o600)
    os.replace(CONF + ".tmp", CONF)
    print("Saved. Restarting the screen's data server...")
    subprocess.run(["systemctl", "--user", "restart", "kitchen"])
    print("The first pick downloads a few hundred photos over the next 10-15 minutes.\n"
          "Check progress any time:  python3 ~/kitchen_screen/pi/check.py")
    time.sleep(1)


if __name__ == "__main__":
    main()
