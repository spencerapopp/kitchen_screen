"""Word of the day: one word per day, never the same word twice.

The word list lives in words.json (repo root). Every word shown is logged in
~/kitchen-data/wotd_history.json; a word counts as used if its English OR its Chinese
was shown before, so it can't come back under another heading.

Order of choice for a day:
  1. a holiday word (Lunar New Year, Mid-Autumn, Thanksgiving, Mother's/Father's Day)
  2. an activity word, for the first activity found in today's calendar (party, swim, soccer, ...)
  3. the day's own word from "months"
  4. any other unused word from this month, then "extra", then the rest of the year
Only when every word has been used does it reuse one: the one shown longest ago.
"""
import json
import os
from datetime import date, timedelta

WEEKDAYS = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}

# Words already shown before this log existed (the card ran from Sept 27, 2026 with
# 7-word activity rotations). Month words for those dates are added automatically.
FIRST_SHOWN = date(2026, 9, 27)
SHOWN_BEFORE_LOG = [
    "pool", "goggles", "splash", "kickboard", "dive", "swimsuit", "lifeguard",           # swim
    "ball", "goal", "team", "whistle", "coach", "cleats", "field",                        # soccer
    "birthday", "cake", "confetti", "invitation",                                         # party
    "stethoscope",                                                                        # doctor
]
LOW_STOCK = 45                     # warn when fewer new words than this are left


def load_bank(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _k(w):
    return w[0].strip().lower(), w[1].strip()


def _all_words(bank):
    for m in bank["months"]:
        yield from m
    yield from bank.get("extra", [])
    for a in bank["activities"].values():
        yield from a["words"]
    for h in bank["holidays"].values():
        yield from h["words"]


def nth_weekday(year, month, weekday, n):
    d = date(year, month, 1)
    d += timedelta(days=(weekday - d.weekday()) % 7)
    return d + timedelta(weeks=n - 1)


def holiday_on(bank, d):
    for h in bank["holidays"].values():
        if d.isoformat() in h.get("dates", []):
            return h
        r = h.get("rule")
        if r and d.month == r["month"] and d == nth_weekday(d.year, r["month"], WEEKDAYS[r["weekday"]], r["nth"]):
            return h
    return None


def activities_in(bank, titles):
    text = " ".join(titles).lower()
    return [k for k, a in bank["activities"].items() if any(kw in text for kw in a["keywords"])]


def new_history(bank, today):
    """Start the log, marking what the old card already showed."""
    by_en = {w[0].lower(): w for w in _all_words(bank)}
    seed = [list(_k(by_en[e])) for e in SHOWN_BEFORE_LOG if e in by_en]
    d = FIRST_SHOWN
    while d < today:
        m = bank["months"][d.month - 1]
        if d.day - 1 < len(m):
            seed.append(list(_k(m[d.day - 1])))
        d += timedelta(days=1)
    return {"seed": seed, "days": {}}


def used_keys(history, skip_day=None):
    en, zh = set(), set()
    for e, z in history.get("seed", []):
        en.add(e); zh.add(z)
    for day, v in history.get("days", {}).items():
        if day != skip_day:
            e, z = _k(v["word"])
            en.add(e); zh.add(z)
    return en, zh


def choose(bank, d, titles, history):
    """Returns (word, label, kind) for date d."""
    en, zh = used_keys(history, skip_day=d.isoformat())
    fresh = lambda w: _k(w)[0] not in en and _k(w)[1] not in zh
    first = lambda ws: next((w for w in ws if fresh(w)), None)

    h = holiday_on(bank, d)
    if h and (w := first(h["words"])):
        return w, h["name"], "holiday"
    for key in activities_in(bank, titles):
        a = bank["activities"][key]
        if w := first(a["words"]):
            return w, a["label"], "activity"

    months = bank["months"]
    m, i = d.month - 1, d.day - 1
    month = months[m]
    rest_of_month = month[i:] + month[:i]
    later_months = [w for j in range(1, 12) for w in months[(m + j) % 12]]
    for pool in (rest_of_month, bank.get("extra", []), later_months,
                 [w for a in bank["activities"].values() for w in a["words"]]):
        if w := first(pool):
            return w, "Word of the day", "day"

    # Every word has been used: repeat the one shown longest ago.
    days = sorted(history.get("days", {}).items())
    w = days[0][1]["word"] if days else month[i % len(month)]
    return w, "Word of the day", "repeat"


def words_left(bank, history):
    en, zh = used_keys(history)
    general = [w for m in bank["months"] for w in m] + bank.get("extra", [])
    return sum(1 for w in general if _k(w)[0] not in en and _k(w)[1] not in zh)


def today_word(bank_path, history_path, d, titles):
    """Pick (or recall) today's word, log it, and return the dict for word.json."""
    bank = load_bank(bank_path)
    if os.path.exists(history_path):
        with open(history_path, encoding="utf-8") as f:
            history = json.load(f)
    else:
        history = new_history(bank, d)
    key = d.isoformat()
    if key not in history["days"]:
        w, label, kind = choose(bank, d, titles, history)
        history["days"][key] = {"word": w, "label": label, "kind": kind}
        tmp = history_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=1)
        os.replace(tmp, history_path)
    entry = history["days"][key]
    left = words_left(bank, history)
    return {"date": key, "word": entry["word"], "label": entry["label"], "kind": entry["kind"],
            "words_left": left,
            "warning": f"Word list: {left} new words left" if left < LOW_STOCK else None}
