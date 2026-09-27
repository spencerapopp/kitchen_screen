"""Build events.json for the kitchen display from private Google Calendar feeds.

Reads one or more secret iCal addresses from the ICAL_URLS environment variable
(one per line) and writes only what the board needs. This repo is public, so the
output is kept deliberately small:

  - "today":      activity keywords found in today's events (e.g. "swim", "soccer").
                  No titles, times, or places.
  - "countdowns": title and date of upcoming events whose title contains "birthday"
                  or the tag "#countdown" (the tag is removed). Nothing else is published.
"""
import json
import os
import re
import sys
import urllib.request
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import icalendar
import recurring_ical_events

TZ = ZoneInfo("America/Chicago")
LOOKAHEAD_DAYS = 120
MAX_COUNTDOWNS = 8

# Keyword in an event title -> activity the word of the day can theme on.
ACTIVITIES = {
    "swim": "swim",
    "soccer": "soccer",
    "basketball": "basketball",
    "birthday": "birthday",
    "dentist": "dentist",
    "doctor": "doctor",
    "pediatric": "doctor",
    "checkup": "doctor",
    "check-up": "doctor",
}
ORDER = ["birthday", "swim", "soccer", "basketball", "dentist", "doctor"]


def fetch(url: str) -> icalendar.Calendar:
    req = urllib.request.Request(url, headers={"User-Agent": "kitchen-screen"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return icalendar.Calendar.from_ical(r.read())


def start_date(ev) -> date:
    dt = ev.get("DTSTART").dt
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=TZ)
        return dt.astimezone(TZ).date()
    return dt


def main() -> int:
    urls = [u.strip() for u in os.environ.get("ICAL_URLS", "").splitlines() if u.strip()]
    if not urls:
        print("ICAL_URLS is not set yet — skipping. Add it under Settings → Secrets → Actions.")
        return 0

    today = datetime.now(TZ).date()
    end = today + timedelta(days=LOOKAHEAD_DAYS)
    todays, counts, failures = set(), {}, 0

    for n, url in enumerate(urls, 1):
        try:
            cal = fetch(url)
        except Exception as e:  # keep going if one calendar is unreachable
            failures += 1
            print(f"calendar {n}: could not be read ({type(e).__name__})")
            continue
        events = recurring_ical_events.of(cal).between(today, end + timedelta(days=1))
        for ev in events:
            title = str(ev.get("SUMMARY", "")).strip()
            low = title.lower()
            day = start_date(ev)
            if day == today:
                for key, act in ACTIVITIES.items():
                    if key in low:
                        todays.add(act)
            if "birthday" in low or "#countdown" in low:
                clean = re.sub(r"\s*#countdown\b", "", title, flags=re.I).strip()
                if clean and today <= day <= end:
                    counts.setdefault((day, clean), None)
        print(f"calendar {n}: read OK")

    if failures == len(urls):
        print("No calendars could be read; leaving events.json unchanged.")
        return 1

    out = {
        "asOf": today.isoformat(),
        "today": [a for a in ORDER if a in todays],
        "countdowns": [{"title": t, "date": d.isoformat()} for d, t in sorted(counts)][:MAX_COUNTDOWNS],
    }
    path = os.path.join(os.path.dirname(__file__), "..", "events.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"today={out['today']} countdowns={len(out['countdowns'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
