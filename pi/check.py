#!/usr/bin/env python3
"""Kitchen screen health report. Shows what's set up, what's working, and what's missing.
Never prints secrets.   Run:  python3 ~/kitchen_screen/pi/check.py
"""
import json
import os
import subprocess
import time
from datetime import datetime

HOME = os.path.expanduser("~")
CONF = os.path.join(HOME, ".config/kitchen/config.json")
DATA = os.path.join(HOME, "kitchen-data")
REPO = os.path.join(HOME, "kitchen_screen")
OK, BAD, MEH = "OK  ", "FIX ", "--  "


def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return ""


def data(name):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return None, None
    try:
        return json.load(open(p)), (time.time() - os.path.getmtime(p)) / 60
    except Exception:
        return {}, None


def age(m):
    return "never" if m is None else f"{m:.0f} min ago" if m < 120 else f"{m / 60:.0f} h ago"


def main():
    cfg = json.load(open(CONF)) if os.path.exists(CONF) else {}
    rows = []
    add = lambda status, what, detail="": rows.append((status, what, detail))

    add(OK if sh("systemctl --user is-active kitchen") == "active" else BAD, "data server", sh("systemctl --user is-active kitchen"))
    add(MEH, "code version", sh(f"git -C {REPO} log -1 --format='%h %cd' --date=format:'%b %d %H:%M'"))
    t = sh("vcgencmd get_throttled 2>/dev/null")
    add(OK if t.endswith("=0x0") else BAD, "power", t or "n/a")
    add(MEH, "temperature", sh("vcgencmd measure_temp 2>/dev/null"))
    add(OK if os.path.exists(os.path.join(HOME, ".local/share/icons/kitchen-blank")) else BAD, "hidden pointer",
        "installed" if os.path.exists(os.path.join(HOME, ".local/share/icons/kitchen-blank")) else "run pi/hide_cursor.py")

    g = cfg.get("google") or {}
    add(OK if g.get("refresh_token") else BAD, "Google sign-in", "connected" if g.get("refresh_token") else "run pi/google_auth.py")
    for f, label in [("calendar.json", "calendar"), ("tasks.json", "family list"), ("photos.json", "photos"),
                     ("weather.json", "weather"), ("word.json", "word of the day"), ("quote.json", "Olivia quote")]:
        d, m = data(f)
        err = (d or {}).get("error") or (d or {}).get("warning")
        add(BAD if d is None or err else OK, label, f"updated {age(m)}" + (f" | {err}" if err else ""))
    tl, _ = data("tasks.json")
    add(MEH, "family list source", "Google Keep" if (tl or {}).get("source") == "keep" else "Google Tasks")
    k = cfg.get("keep") or {}
    add(OK if k.get("master_token") else MEH, "Google Keep",
        f"{k.get('email')} -> '{k.get('family_list')}', '{k.get('quotes_note')}'" if k.get("master_token") else "not set up (pi/keep_auth.py)")
    w, _ = data("word.json")
    if w:
        add(MEH, "today's word", f"{w['word'][0]} {w['word'][1]} ({w['label']}), {w.get('words_left')} new words left")

    add(OK if cfg.get("home_address") else BAD, "home address", "set" if cfg.get("home_address") else "MISSING: no drive times")
    add(OK if cfg.get("commute") else BAD, "commute places",
        ", ".join(c.get("name", "?") for c in cfg.get("commute") or []) or "MISSING: no morning commute strip")
    add(OK if cfg.get("tomtom_key") else MEH, "live traffic", "TomTom key set" if cfg.get("tomtom_key") else "no key: usual drive times only")
    mt = cfg.get("morning_trip")
    add(OK if mt else MEH, "morning trip",
        f"{mt.get('name', '')}: {mt.get('via_name', '') + ' (by ' + mt.get('via_by', '') + ') -> ' if mt.get('via') else ''}"
        f"{mt.get('to_name', 'work')} by {mt.get('by', '08:30')}" if mt else "not set (leave-by time for drop-off + work)")
    c, m = data("commute.json")
    add(BAD if (c or {}).get("error") else MEH, "commute strip",
        f"{'showing' if (c or {}).get('show') else 'hidden (shows Mon-Fri ' + '-'.join(cfg.get('commute_hours') or ['06:30', '09:30']) + ')'}"
        + (f" | leave {c['trip']['leave'][11:16]}" if (c or {}).get("trip") else "")
        + (f" | {c['error']}" if (c or {}).get("error") else ""))
    lv, m = data("leave.json")
    trips = (lv or {}).get("trips") or []
    add(BAD if (lv or {}).get("error") else MEH, "leave-by banner",
        (f"next: {trips[0]['title']} leave {trips[0]['leave'][11:16]}" if trips else "nothing within 3 h")
        + (f" | {lv['error']}" if (lv or {}).get("error") else ""))
    add(MEH, "leave-by events", ", ".join(cfg.get("leave_titles") or []) or "none (add '#leave' to an event title)")

    print(f"\nKitchen screen check — {datetime.now():%a %b %d %H:%M}\n")
    for s, w_, d in rows:
        print(f"  {s} {w_:<20} {d}")
    print("\nFIX lines need attention. Logs:  journalctl --user -u kitchen -n 40 --no-pager\n")


if __name__ == "__main__":
    main()
