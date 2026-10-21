#!/usr/bin/env python3
"""Kitchen dashboard server for the Raspberry Pi.

Serves the dashboard at http://localhost:8080/pi/dashboard.html and keeps three
small data files fresh in ~/kitchen-data (served at /data/):

  calendar.json  events from Google Calendar                    (every 30 seconds)
  tasks.json     open items on your Google Tasks family list   (every 15 seconds)
  photos.json    photos from the Google Drive "Kitchen Photos" folder, converted
                 to JPEG and resized, cached in ~/kitchen-data/photos/  (every 5 minutes)
  alerts.json    National Weather Service warnings/watches for home (every minute)
  leave.json     "leave by" times for events with an address in the next 3 hours
  commute.json   weekday-morning drive times to the places in config "commute"

Private settings (calendar addresses, Google sign-in) live only on the Pi in
~/.config/kitchen/config.json — never in the GitHub repo.
"""
import io
import json
import os
import re
import sys
import threading
import time
import traceback
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from zoneinfo import ZoneInfo

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.expanduser("~/kitchen-data")
PHOTOS = os.path.join(DATA, "photos")
CONFIG = os.path.expanduser("~/.config/kitchen/config.json")
TZ = ZoneInfo("America/Chicago")
PORT = 8080
WEEKS = 5
PHOTO_MAX = 1600          # longest side, pixels
MAX_PHOTOS = 1000


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def load_config():
    try:
        with open(CONFIG) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


_last = {}


def write_json(name, obj):
    """Write a data file only when its content changed (spares the SD card)."""
    key = json.dumps({k: v for k, v in obj.items() if k != "updated"}, sort_keys=True)
    if _last.get(name) == key and os.path.exists(os.path.join(DATA, name)):
        return False
    _last[name] = key
    tmp = os.path.join(DATA, name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, os.path.join(DATA, name))
    return True


def http(url, data=None, headers=None, timeout=30):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "kitchen-screen", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# ── calendar ────────────────────────────────────────────────────────────────
# With Google connected, events come straight from the Calendar API — changes
# show up within ~30 seconds. Without it, the secret iCal address is used; Google
# refreshes that feed on its own schedule, so changes can take a while to appear.
_ical = {"next": 0}
_events = []          # latest events, shared with the drive-time checker
_cal = {"ready": False}   # set once the first calendar load succeeds


def window():
    today = datetime.now(TZ).date()
    start = today - timedelta(days=(today.weekday() + 1) % 7)       # Sunday of this week
    return start, start + timedelta(days=WEEKS * 7 + 1)


def is_leave(cfg, title):
    t = title.lower()
    return "#leave" in t or any(x.lower() == t.strip() for x in cfg.get("leave_titles") or [])


# Google Calendar's event colours (colorId -> hex), as shown in the Calendar app.
EVENT_COLORS = {"1": "#7986CB", "2": "#33B679", "3": "#8E24AA", "4": "#E67C73", "5": "#F6BF26", "6": "#F4511E",
                "7": "#039BE5", "8": "#616161", "9": "#3F51B5", "10": "#0B8043", "11": "#D50000"}


# Colour by title when an event has no colour of its own (keyword -> hex). Override with "event_colors" in config.
KEYWORD_COLORS = {"soccer": "#8E24AA", "swim": "#039BE5", "gymnast": "#E67C73"}


def keyword_color(cfg, title):
    rules = cfg.get("event_colors") or KEYWORD_COLORS
    t = title.lower()
    return next((c for k, c in rules.items() if k.lower() in t), None)


def calendar_from_api(cfg):
    start, end = window()
    cals = json.loads(gget(cfg, "https://www.googleapis.com/calendar/v3/users/me/calendarList?maxResults=250")).get("items", [])
    names = [n.lower() for n in (cfg.get("calendar_names") or [])]
    chosen = [c for c in cals if c.get("summary", "").lower() in names] or [c for c in cals if c.get("primary")]
    # Your own (primary) calendar is also read for hidden "#leave" events, even if it isn't shown.
    leave_only = [c for c in cals if c.get("primary") and c not in chosen]
    out = []
    t0 = datetime.combine(start, datetime.min.time(), TZ).isoformat()
    t1 = datetime.combine(end, datetime.min.time(), TZ).isoformat()
    for c in chosen + leave_only:
        page = ""
        while True:
            url = ("https://www.googleapis.com/calendar/v3/calendars/" + urllib.parse.quote(c["id"]) +
                   "/events?singleEvents=true&orderBy=startTime&maxResults=2500"
                   "&timeMin=" + urllib.parse.quote(t0) + "&timeMax=" + urllib.parse.quote(t1) + page)
            r = json.loads(gget(cfg, url))
            for ev in r.get("items", []):
                if ev.get("status") == "cancelled":
                    continue
                title = (ev.get("summary") or "(busy)").strip()
                if c in leave_only and not is_leave(cfg, title):
                    continue
                st, en = ev.get("start", {}), ev.get("end", {})
                # The event's own colour, else None (the screen uses its default look).
                color = EVENT_COLORS.get(str(ev.get("colorId", ""))) or keyword_color(cfg, title)
                if "dateTime" in st:
                    s = datetime.fromisoformat(st["dateTime"]).astimezone(TZ)
                    out.append({"title": title, "start": s.isoformat(), "allDay": False,
                                "location": (ev.get("location") or "").strip(), "color": color,
                                "free": ev.get("transparency") == "transparent"})
                elif "date" in st:
                    out.append({"title": title, "start": st["date"], "end": en.get("date") or st["date"], "allDay": True,
                                "color": color})
            if not r.get("nextPageToken"):
                break
            page = "&pageToken=" + r["nextPageToken"]
    if cfg.get("holidays", True):
        mine = {}
        for ev in out:                                   # skip a holiday the family calendar already has that day
            mine.setdefault(ev["start"][:10], []).append(ev["title"].lower())
        for h in holidays(cfg, t0, t1):
            words = [w for w in re.findall(r"[a-z']+", h["title"].lower()) if len(w) > 3][:2]
            if not any(all(w in t for w in words) or ("daylight" in t and "clocks" in h["title"].lower())
                       for t in mine.get(h["start"], [])):
                out.append(h)
    return out, []


# Family-worthy holidays from Google's public holiday calendars: {calendar: {holiday name: (shown as, colour)}}
HOLIDAYS = {
    "en.usa#holiday@group.v.calendar.google.com": {
        "New Year's Day": ("New Year's Day", "#F6BF26"), "Valentine's Day": ("Valentine's Day", "#E67C73"),
        "St. Patrick's Day": ("St. Patrick's Day", "#33B679"), "Easter Sunday": ("Easter", "#7986CB"),
        "Mother's Day": ("Mother's Day", "#E67C73"), "Memorial Day": ("Memorial Day", "#3F51B5"),
        "Father's Day": ("Father's Day", "#039BE5"), "Independence Day": ("4th of July", "#3F51B5"),
        "Labor Day": ("Labor Day", "#616161"), "Halloween": ("Halloween", "#F4511E"),
        "Thanksgiving Day": ("Thanksgiving", "#F4511E"), "Christmas Eve": ("Christmas Eve", "#0B8043"),
        "Christmas Day": ("Christmas", "#0B8043"), "New Year's Eve": ("New Year's Eve", "#F6BF26"),
        "Daylight Saving Time starts": ("Spring Forward (clocks +1 hr)", "#616161"),
        "Daylight Saving Time ends": ("Fall Back (clocks −1 hr)", "#616161"),
    },
    "en.china#holiday@group.v.calendar.google.com": {
        "Spring Festival Eve": ("Lunar New Year's Eve", "#D50000"), "Chinese New Year": ("Lunar New Year", "#D50000"),
        "Lantern Festival": ("Lantern Festival", "#D50000"), "Dragon Boat Festival": ("Dragon Boat Festival", "#33B679"),
        "Mid-Autumn Festival": ("Mid-Autumn Festival", "#F6BF26"),
    },
}
_hol = {}   # calendar -> (fetched at, window start, events)


def holidays(cfg, t0, t1):
    """Holiday events for the calendar window, refreshed twice a day. Never breaks the calendar."""
    out = []
    for cal, keep in HOLIDAYS.items():
        at, key, evs = _hol.get(cal, (0, "", []))
        if key != t0 or time.time() - at > 12 * 3600:
            try:
                url = ("https://www.googleapis.com/calendar/v3/calendars/" + urllib.parse.quote(cal) +
                       "/events?singleEvents=true&maxResults=250&timeMin=" + urllib.parse.quote(t0) +
                       "&timeMax=" + urllib.parse.quote(t1))
                evs = []
                for ev in json.loads(gget(cfg, url)).get("items", []):
                    name = (ev.get("summary") or "").strip()
                    st = (ev.get("start") or {}).get("date")
                    if name in keep and st:
                        title, color = keep[name]
                        evs.append({"title": title, "start": st[:10], "end": ((ev.get("end") or {}).get("date") or st)[:10],
                                    "allDay": True, "color": color, "holiday": True})
                _hol[cal] = (time.time(), t0, evs)
            except Exception as e:
                log("holidays:", cal.split("#")[0], e)    # keep the last good list for this calendar
        out += evs
    return out


def calendar_from_ical(cfg):
    import icalendar
    import recurring_ical_events
    start, end = window()
    out, errors = [], []
    for n, url in enumerate(cfg.get("ical_urls") or [], 1):
        try:
            cal = icalendar.Calendar.from_ical(http(url))
            for ev in recurring_ical_events.of(cal).between(start, end):
                title = str(ev.get("SUMMARY", "")).strip() or "(busy)"
                s = ev.get("DTSTART").dt
                e = ev.get("DTEND").dt if ev.get("DTEND") else None
                if isinstance(s, datetime):
                    s = s.astimezone(TZ) if s.tzinfo else s.replace(tzinfo=TZ)
                    out.append({"title": title, "start": s.isoformat(), "allDay": False,
                                "location": str(ev.get("LOCATION", "") or "").strip(),
                                "color": keyword_color(cfg, title)})
                else:
                    out.append({"title": title, "start": s.isoformat(),
                                "end": (e if isinstance(e, date) and not isinstance(e, datetime) else s + timedelta(days=1)).isoformat(),
                                "allDay": True})
        except Exception as ex:
            errors.append(f"calendar {n}: {type(ex).__name__}")
    return out, errors


def update_calendar(cfg):
    has_api = google_token(cfg) and "calendar" in (cfg.get("google") or {}).get("scopes", "")
    if has_api:
        out, errors = calendar_from_api(cfg)
    else:
        if not cfg.get("ical_urls"):
            write_json("calendar.json", {"events": [], "error": "no calendars set up"})
            return
        if time.time() < _ical["next"]:
            return
        _ical["next"] = time.time() + 180                   # the iCal feed: every 3 minutes
        out, errors = calendar_from_ical(cfg)
    # "#leave" events (and titles listed in leave_titles) drive the leave-by banner only;
    # they're never drawn on the calendar.
    for ev in out:
        if is_leave(cfg, ev["title"]):
            ev["hidden"] = True
            ev["title"] = " ".join(w for w in ev["title"].split() if w.lower() != "#leave")
    # Same event on two calendars (e.g. shared family events) → show once.
    seen, unique = set(), []
    for ev in sorted(out, key=lambda x: x["start"]):
        k = (ev["title"].lower(), ev["start"])
        if k not in seen:
            seen.add(k)
            unique.append(ev)
    if errors and not unique:
        return log("calendar failed:", errors)          # keep the last good file
    _events[:] = unique
    _cal["ready"] = True
    if write_json("calendar.json", {"updated": datetime.now(TZ).isoformat(), "events": unique,
                                    "error": ", ".join(errors) or None}):
        log(f"calendar: {len(unique)} events ({'Google' if has_api else 'iCal'})")


# ── Google sign-in (one refresh token, set up once with google_auth.py) ─────
_token = {"value": None, "expires": 0}


def google_token(cfg):
    g = cfg.get("google") or {}
    if not g.get("refresh_token"):
        return None
    if _token["value"] and time.time() < _token["expires"] - 60:
        return _token["value"]
    body = urllib.parse.urlencode({
        "client_id": g["client_id"], "client_secret": g["client_secret"],
        "refresh_token": g["refresh_token"], "grant_type": "refresh_token"}).encode()
    r = json.loads(http("https://oauth2.googleapis.com/token", data=body))
    _token.update(value=r["access_token"], expires=time.time() + r.get("expires_in", 3600))
    return _token["value"]


def gget(cfg, url):
    return http(url, headers={"Authorization": "Bearer " + google_token(cfg)})


# ── family list ─────────────────────────────────────────────────────────────
def update_tasks(cfg):
    if keep_cfg(cfg) and (cfg["keep"].get("family_list") or "Family List"):
        return                                          # the Family List comes from Google Keep instead
    if not google_token(cfg):
        write_json("tasks.json", {"items": [], "error": "Google not connected yet"})
        return
    lists = json.loads(gget(cfg, "https://tasks.googleapis.com/tasks/v1/users/@me/lists?maxResults=100")).get("items", [])
    want = (cfg.get("tasks_list") or "").lower()
    chosen = next((l for l in lists if l["title"].lower() == want), None) or (lists[0] if lists else None)
    if not chosen:
        write_json("tasks.json", {"items": [], "error": "no task lists found"})
        return
    items, page = [], ""
    while True:
        url = (f"https://tasks.googleapis.com/tasks/v1/lists/{chosen['id']}/tasks"
               f"?showCompleted=false&showHidden=false&maxResults=100{page}")
        r = json.loads(gget(cfg, url))
        items += [t for t in r.get("items", []) if t.get("title", "").strip() and not t.get("parent")]
        if not r.get("nextPageToken"):
            break
        page = "&pageToken=" + r["nextPageToken"]
    items.sort(key=lambda t: t.get("position", ""))
    if write_json("tasks.json", {"title": cfg.get("tasks_title") or chosen["title"],
                                 "items": [t["title"].strip() for t in items]}):
        log(f"tasks: {len(items)} open on '{chosen['title']}'")


# ── photos ──────────────────────────────────────────────────────────────────
def find_folder(cfg):
    if cfg.get("photos_folder_id"):
        return cfg["photos_folder_id"]
    name = (cfg.get("photos_folder") or "Kitchen Photos").replace("'", "\\'")
    q = urllib.parse.quote(f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false")
    r = json.loads(gget(cfg, f"https://www.googleapis.com/drive/v3/files?q={q}&fields=files(id,name)"))
    return r["files"][0]["id"] if r.get("files") else None


def to_jpeg(raw):
    from PIL import Image, ImageOps
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
    except ImportError:
        pass
    im = Image.open(io.BytesIO(raw))
    im = ImageOps.exif_transpose(im).convert("RGB")      # respect phone rotation
    im.thumbnail((PHOTO_MAX, PHOTO_MAX))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=86, optimize=True)
    return buf.getvalue()


def update_photos(cfg):
    if not google_token(cfg):
        write_json("photos.json", {"photos": [], "error": "Google not connected yet"})
        return
    folder = find_folder(cfg)
    if not folder:
        write_json("photos.json", {"photos": [], "error": "Kitchen Photos folder not found"})
        return
    files, page = [], ""
    while True:
        q = urllib.parse.quote(f"'{folder}' in parents and trashed = false and "
                               "(mimeType contains 'image/' or name contains '.HEIC' or name contains '.heic')")
        r = json.loads(gget(cfg, f"https://www.googleapis.com/drive/v3/files?q={q}&pageSize=200"
                                 f"&fields=nextPageToken,files(id,name,modifiedTime){page}"))
        files += r.get("files", [])
        if not r.get("nextPageToken") or len(files) >= MAX_PHOTOS:
            break
        page = "&pageToken=" + r["nextPageToken"]
    os.makedirs(PHOTOS, exist_ok=True)
    keep, added, failed = [], 0, 0
    for f in files[:MAX_PHOTOS]:
        path = os.path.join(PHOTOS, f["id"] + ".jpg")
        if not os.path.exists(path):
            try:
                jpg = to_jpeg(gget(cfg, f"https://www.googleapis.com/drive/v3/files/{f['id']}?alt=media"))
                with open(path + ".tmp", "wb") as out:
                    out.write(jpg)
                os.replace(path + ".tmp", path)
                added += 1
            except Exception as ex:
                failed += 1
                log("photo failed:", f["name"], type(ex).__name__, ex)
                continue
        keep.append("photos/" + f["id"] + ".jpg")
    # Photos removed from the Drive folder disappear from the screen too.
    wanted = {os.path.basename(k) for k in keep}
    for name in os.listdir(PHOTOS):
        if name.endswith(".jpg") and name not in wanted:
            os.remove(os.path.join(PHOTOS, name))
    write_json("photos.json", {"photos": keep, "seconds": int(cfg.get("photo_seconds", 20)),
                                "error": f"{failed} photos could not be read" if failed else None})
    log(f"photos: {len(keep)} ({added} new)")



# ── weather (Open-Meteo, free, no key) ─────────────────────────────────────
def update_weather(cfg):
    lat, lng = cfg.get("lat", 33.0198), cfg.get("lng", -96.6989)
    url = ("https://api.open-meteo.com/v1/forecast?latitude=%s&longitude=%s"
           "&current=temperature_2m,weather_code&daily=weather_code,temperature_2m_max,temperature_2m_min"
           "&temperature_unit=fahrenheit&timezone=America%%2FChicago&forecast_days=5" % (lat, lng))
    w = json.loads(http(url))
    if write_json("weather.json", {"current": w["current"], "daily": w["daily"]}):
        log("weather:", round(w["current"]["temperature_2m"]), "F")


# ── air quality + pollen (small color-coded chips under the temperature) ────
# Air: Open-Meteo (US AQI, free, no key). Pollen: Pollen.com's forecast for the home ZIP
# (free, no key, unofficial). Refreshed every 30 minutes; a failure keeps the last reading.
AQI_LEVELS = [(50, "Good", 0), (100, "Moderate", 1), (150, "Sensitive", 2), (200, "Unhealthy", 3),
              (300, "Very unhealthy", 4), (10_000, "Hazardous", 5)]
POLLEN_LEVELS = [(2.4, "Low", 0), (4.8, "Low-Med", 0), (7.2, "Medium", 1), (9.6, "Med-High", 2), (12.1, "High", 3)]
_air = {"at": 0, "aqi": None, "pollen": None, "aqi_at": 0, "pollen_at": 0}


def home_zip(cfg):
    m = re.search(r"\b(\d{5})(?:-\d{4})?\s*$", cfg.get("home_address", "").strip())
    return cfg.get("zip") or (m.group(1) if m else None)


def pollen_today(z):
    r = json.loads(http(f"https://www.pollen.com/api/forecast/current/pollen/{z}",
                        headers={"Referer": f"https://www.pollen.com/forecast/current/pollen/{z}",
                                 "User-Agent": "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36",
                                 "Accept": "application/json"}))
    periods = (r.get("Location") or {}).get("periods") or []
    today = next((x for x in periods if x.get("Type") == "Today"), periods[1] if len(periods) > 1 else None)
    if not today or today.get("Index") is None:
        raise ValueError("no pollen forecast for today")
    idx = float(today["Index"])
    word, lvl = next((w, l) for top, w, l in POLLEN_LEVELS if idx <= top)
    trig = today.get("Triggers") or []
    trig = trig.values() if isinstance(trig, dict) else trig
    names = [t.get("Name") for t in trig if isinstance(t, dict) and t.get("Name")]
    return {"index": round(idx, 1), "level": word, "lvl": lvl, "triggers": names[:3]}


def update_air(cfg):
    now = time.time()
    if now - _air["at"] < 30 * 60:
        return
    _air["at"] = now
    lat, lng = cfg.get("lat", 33.0198), cfg.get("lng", -96.6989)
    err = []
    try:
        r = json.loads(http(f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lng}"
                            "&current=us_aqi&timezone=America%2FChicago"))
        v = r["current"]["us_aqi"]
        if v is not None:
            v = round(v)
            word, lvl = next((w, l) for top, w, l in AQI_LEVELS if v <= top)
            _air.update(aqi={"value": v, "level": word, "lvl": lvl}, aqi_at=now)
    except Exception as e:
        err.append(f"air quality: {type(e).__name__} {str(e)[:80]}")
    z = home_zip(cfg)
    if z and cfg.get("pollen", True):
        try:
            _air.update(pollen=pollen_today(z), pollen_at=now)
        except Exception as e:
            err.append(f"pollen: {type(e).__name__} {str(e)[:80]}")
    for k in ("aqi", "pollen"):                       # a reading older than 6 hours is dropped
        if _air[k] and now - _air[k + "_at"] > 6 * 3600:
            _air[k] = None
    if err:
        log("air:", "; ".join(err))
        _air["at"] = now - 25 * 60                    # a failure is retried in 5 minutes, not 30
    write_json("air.json", {"aqi": _air["aqi"], "pollen": _air["pollen"],
                            "error": ("no " + " / ".join(e.split(":")[0] for e in err) + " data") if err and not (_air["aqi"] and _air["pollen"]) else None})


# ── countdown: one at a time, shown in the banner spot when nothing else is there ──
# Holidays come built in. Family birthdays: "birthdays": {"Olivia": "MM-DD", ...} in config.json.
# Trips come from the calendar (titles with "trip" or "vacation").
LUNAR_NEW_YEAR = {2027: "02-06", 2028: "01-26", 2029: "02-13", 2030: "02-03", 2031: "01-23", 2032: "02-11"}


def easter(y):
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    g = (8 * b + 13) // 25
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 19 * l + 433) // 432
    mo = (h + l - 7 * m + 90) // 25
    return date(y, mo, (h + l - 7 * m + 33 * mo + 19) % 32)


def nth_weekday(y, mo, wd, n):
    d = date(y, mo, 1)
    return d + timedelta(days=(wd - d.weekday()) % 7 + 7 * (n - 1))


COUNTDOWN_HOLIDAYS = [   # name, icon, days ahead it starts showing, date for a year
    ("Halloween", "pumpkin", 30, lambda y: date(y, 10, 31)),
    ("Thanksgiving", "leaf", 25, lambda y: nth_weekday(y, 11, 3, 4)),
    ("Christmas", "tree", 30, lambda y: date(y, 12, 25)),
    ("Lunar New Year", "lantern", 21, lambda y: date.fromisoformat(f"{y}-{LUNAR_NEW_YEAR[y]}") if y in LUNAR_NEW_YEAR else None),
    ("Valentine's Day", "heart", 10, lambda y: date(y, 2, 14)),
    ("Easter", "egg", 14, easter),
    ("Fourth of July", "star", 10, lambda y: date(y, 7, 4)),
]
TRIP = re.compile(r"\btrip\b|vacation", re.I)


def countdown_candidates(cfg, today):
    out = []
    for name, icon, window, fn in COUNTDOWN_HOLIDAYS:
        for y in (today.year, today.year + 1):
            d = fn(y)
            if d and 0 <= (d - today).days <= window:
                out.append({"label": name, "icon": icon, "kind": "holiday", "days": (d - today).days})
    for who, v in (cfg.get("birthdays") or {}).items():
        b = v if isinstance(v, dict) else {"date": v}     # "YYYY-MM-DD" / "MM-DD", or {"date", "label", "today"}
        parts = b.get("date", "").split("-")
        try:
            born = int(parts[0]) if len(parts) == 3 else None
            m, dd = map(int, parts[-2:])
            d = date(today.year, m, dd)
            if d < today:
                d = date(today.year + 1, m, dd)
        except ValueError:
            continue
        if (d - today).days > 45 or (b.get("surprise") and d != today):
            continue                                   # "surprise": true shows only on the day itself
        age = d.year - born if born else None
        kid = age is not None and age < 18
        nth = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"
        out.append({"label": b.get("label") or (f"{who} turns {age}" if kid else f"{who}'s birthday"),
                    "today": b.get("today") or (f"Happy {nth(age)} birthday, {who}!" if kid else f"Happy birthday, {who}!"),
                    "icon": "gift", "kind": "birthday", "days": (d - today).days})
    seen = set()
    for ev in sorted(_events, key=lambda e: e["start"]):
        title = re.sub(r"[^\w&'’\-–—,. ]+", "", ev["title"]).strip(" -–—")
        if not TRIP.search(title) or title.lower() in seen:
            continue
        seen.add(title.lower())
        d = date.fromisoformat(ev["start"][:10])
        if 0 <= (d - today).days <= 60:
            out.append({"label": title, "icon": "plane", "kind": "trip", "days": (d - today).days})
    return sorted(out, key=lambda c: (c["days"], {"birthday": 0, "holiday": 1, "trip": 2}[c["kind"]]))


def pick_countdown(cands, today):
    """Today's one countdown: anything happening today or within a week wins; otherwise the
    nearest holiday, with a birthday or trip countdown mixed in every third day while that
    holiday is still 2+ weeks away."""
    if not cands:
        return None
    if cands[0]["days"] <= 7:
        return cands[0]
    main = next((c for c in cands if c["kind"] == "holiday"), cands[0])
    others = [c for c in cands if c is not main]
    n = today.toordinal()
    if others and n % 3 == 0 and (main["kind"] != "holiday" or main["days"] >= 14):
        return others[(n // 3) % len(others)]
    return main


# ── weekly school note: "Pre-K this week: Letter N, ..." stays off the calendar grid and shows
# as a quiet note in the banner spot, 4-8 PM on the first two days of its week.
NOTE_TITLE = r"^\s*pre-?k this week\s*[:\-–]\s*"


def update_note(cfg):
    now = datetime.now(TZ)
    pat = re.compile(cfg.get("note_pattern", NOTE_TITLE), re.I)
    a, b = (cfg.get("note_hours") or ["16:00", "20:00"])[:2]
    note = None
    if a <= now.strftime("%H:%M") < b:
        today = now.date()
        for ev in _events:
            if not ev.get("allDay") or not pat.search(ev["title"]):
                continue
            s = date.fromisoformat(ev["start"][:10])
            e = date.fromisoformat((ev.get("end") or ev["start"])[:10])
            if s <= today < e and (today - s).days < 2:
                note = {"show": True, "label": "This week at Pre-K", "text": pat.sub("", ev["title"]).strip(),
                        "icon": "book", "date": today.isoformat()}
                break
    write_json("note.json", note or {"show": False})


def update_countdown(cfg):
    if cfg.get("countdown") is False:
        return write_json("countdown.json", {"show": False})
    today = datetime.now(TZ).date()
    c = pick_countdown(countdown_candidates(cfg, today), today)
    write_json("countdown.json", {"show": bool(c), **(c or {}), "date": today.isoformat()})


# ── severe weather (National Weather Service, free, no key) ────────────────
def update_alerts(cfg):
    lat, lng = cfg.get("lat", 33.0198), cfg.get("lng", -96.6989)
    r = json.loads(http(f"https://api.weather.gov/alerts/active?point={lat},{lng}",
                        headers={"User-Agent": "kitchen-screen (family dashboard)", "Accept": "application/geo+json"}))
    out = []
    for f in r.get("features", []):
        p = f.get("properties", {})
        name = p.get("event", "")
        # Warnings and watches only — advisories (heat, wind) would be on screen all summer.
        if not (name.endswith("Warning") or name.endswith("Watch") or name.endswith("Emergency")):
            continue
        out.append({"event": name, "severity": p.get("severity"),
                    "level": "warning" if not name.endswith("Watch") else "watch",
                    "ends": p.get("ends") or p.get("expires"), "headline": p.get("headline")})
    rank = {"warning": 0, "watch": 1}
    out.sort(key=lambda a: (rank[a["level"]], a["event"]))
    if write_json("alerts.json", {"alerts": out}):
        log("alerts:", [a["event"] for a in out] or "none")


# ── "leave by" drive times ─────────────────────────────────────────────────
# With a free TomTom key (developer.tomtom.com, no credit card) times include live
# traffic. Without one, OpenStreetMap routing gives typical drive times.
LEAVE_WINDOW_H = 3
_geo = {}
_tomtom = {"error": None}   # last TomTom problem, shown on the status line
_drive = {}


ABBREV = {"trl": "Trail", "rd": "Road", "ln": "Lane", "dr": "Drive", "st": "Street", "ave": "Avenue",
          "blvd": "Boulevard", "pkwy": "Parkway", "ct": "Court", "cir": "Circle", "hwy": "Highway", "pl": "Place"}


def expand_abbrev(q):
    return re.sub(r"\b([A-Za-z]+)\.?(?=[ ,]|$)", lambda m: ABBREV.get(m.group(1).lower(), m.group(1)), q)


def geocode(cfg, q):
    if _geo.get(q):
        return _geo[q]
    cache = os.path.join(DATA, "geocache.json")
    if not _geo and os.path.exists(cache):
        _geo.update({k: v for k, v in json.load(open(cache)).items() if v})   # drop old failed lookups
        if _geo.get(q):
            return _geo[q]
    lat, lng = cfg.get("lat", 33.0198), cfg.get("lng", -96.6989)
    pt = None
    key = cfg.get("tomtom_key")
    if key:
        try:
            r = json.loads(http(f"https://api.tomtom.com/search/2/search/{urllib.parse.quote(q)}.json"
                                f"?key={key}&lat={lat}&lon={lng}&radius=80000&limit=1"))
            if r.get("results"):
                p = r["results"][0]["position"]
                pt = [p["lat"], p["lon"]]
            _tomtom["error"] = None
        except Exception as e:
            _tomtom["error"] = tomtom_problem(e)
    if pt is None:
        box = f"{lng-0.8},{lat+0.6},{lng+0.8},{lat-0.6}"          # bias to DFW
        for query in dict.fromkeys([q, expand_abbrev(q)]):          # "6412 Allegheny Trl" -> "... Trail"
            r = json.loads(http("https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=us"
                                "&viewbox=" + box + "&q=" + urllib.parse.quote(query),
                                headers={"User-Agent": "kitchen-screen (family dashboard)"}))
            time.sleep(1.1)                                       # Nominatim: max 1 request/second
            if r:
                pt = [float(r[0]["lat"]), float(r[0]["lon"])]
                break
    if pt is None:
        log("address not found:", q)
        return None                                               # not cached: tried again next time
    _geo[q] = pt
    write_json("geocache.json", dict(_geo))
    return pt


def drive_minutes(cfg, a, b):
    m, live, _ = drive_route(cfg, a, b)
    return m, live


def tomtom_problem(e):
    code = getattr(e, "code", None)
    if code in (401, 403):
        return f"TomTom key rejected ({code}): showing usual drive times"
    return f"TomTom unavailable ({code or type(e).__name__}): showing usual drive times"


def drive_route(cfg, a, b):
    """(minutes now, live traffic?, minutes with no traffic). Falls back to usual times if TomTom fails."""
    key = cfg.get("tomtom_key")
    if key:
        try:
            r = json.loads(http(f"https://api.tomtom.com/routing/1/calculateRoute/{a[0]},{a[1]}:{b[0]},{b[1]}/json"
                                f"?key={key}&traffic=true&travelMode=car&routeType=fastest&computeTravelTimeFor=all"))
            sm = r["routes"][0]["summary"]
            now_m = round(sm["travelTimeInSeconds"] / 60)
            free_m = round(sm.get("noTrafficTravelTimeInSeconds", sm["travelTimeInSeconds"]) / 60)
            _tomtom["error"] = None
            return now_m, True, free_m
        except Exception as e:
            _tomtom["error"] = tomtom_problem(e)
            log(_tomtom["error"])
    r = json.loads(http(f"https://router.project-osrm.org/route/v1/driving/{a[1]},{a[0]};{b[1]},{b[0]}?overview=false",
                        headers={"User-Agent": "kitchen-screen (family dashboard)"}))
    m = round(r["routes"][0]["duration"] / 60 * 1.2)            # OSRM runs optimistic; pad 20%
    return m, False, m



def drive_legs(cfg, pts, depart=None):
    """Minutes for each leg of home -> stop -> ... with traffic. depart: a future datetime (TomTom
    predicts traffic for then). Returns (leg minutes, live?, total minutes with no traffic)."""
    key = cfg.get("tomtom_key")
    if key:
        try:
            when = ""
            if depart and depart > datetime.now(TZ) + timedelta(minutes=2):
                when = "&departAt=" + urllib.parse.quote(depart.isoformat(timespec="seconds"))
            path = ":".join(f"{a},{b}" for a, b in pts)
            r = json.loads(http(f"https://api.tomtom.com/routing/1/calculateRoute/{path}/json"
                                f"?key={key}&traffic=true&travelMode=car&routeType=fastest&computeTravelTimeFor=all{when}"))
            route = r["routes"][0]
            legs = [round(l["summary"]["travelTimeInSeconds"] / 60) for l in route["legs"]]
            sm = route["summary"]
            _tomtom["error"] = None
            return legs, True, round(sm.get("noTrafficTravelTimeInSeconds", sm["travelTimeInSeconds"]) / 60)
        except Exception as e:
            _tomtom["error"] = tomtom_problem(e)
            log(_tomtom["error"])
    path = ";".join(f"{b},{a}" for a, b in pts)
    r = json.loads(http(f"https://router.project-osrm.org/route/v1/driving/{path}?overview=false",
                        headers={"User-Agent": "kitchen-screen (family dashboard)"}))
    legs = [round(l["duration"] / 60 * 1.2) for l in r["routes"][0]["legs"]]
    return legs, False, sum(legs)

NO_SCHOOL = re.compile(r"no school|holiday|school closed|\bclosed\b|\bbreak\b|teacher (work|in-?service)|day off", re.I)


def no_school_days():
    """Dates covered by all-day 'No school' / 'Break' / 'Holiday' events."""
    off = set()
    for ev in _events:
        if ev.get("allDay") and NO_SCHOOL.search(ev["title"]):
            d0 = date.fromisoformat(ev["start"])
            d1 = max(date.fromisoformat(ev.get("end") or ev["start"]), d0 + timedelta(days=1))
            while d0 < d1:
                off.add(d0.isoformat()); d0 += timedelta(days=1)
    return off


def update_leave(cfg):
    home_q = cfg.get("home_address")
    if not home_q:
        write_json("leave.json", {"trips": [], "error": "no home_address in config"})
        return
    home = geocode(cfg, home_q)
    places = {k.lower(): v for k, v in (cfg.get("places") or {}).items()}
    now = datetime.now(TZ)
    buffer = int(cfg.get("leave_buffer_min", 5))
    # Hidden trips (school drop-off) are skipped on days marked "No school", "Holiday", "Closed", etc.
    off_days = no_school_days()
    mt = cfg.get("morning_trip") or []
    covered = {c for t in (mt if isinstance(mt, list) else [mt]) for c in t.get("covers") or []}
    trips = []
    for ev in list(_events):
        loc = ev.get("location")
        if ev.get("allDay") or not loc or ev["title"] in covered:
            continue                                   # covered = handled by the morning trip card
        start = datetime.fromisoformat(ev["start"])
        if not (now < start <= now + timedelta(hours=LEAVE_WINDOW_H)):
            continue
        if (start.date().isoformat() in off_days and
                re.search(r"school|pre-?k|preschool|drop.?off|pick.?up", ev["title"] + " " + loc, re.I)):
            continue                                   # no drop-off on no-school days
        early = int((cfg.get("arrive_early") or {}).get(ev["title"], 0))
        arrive = start - timedelta(minutes=early)
        places = {k.lower(): v for k, v in (cfg.get("places") or {}).items()}
        dest = geocode(cfg, places.get(loc.lower(), loc))
        if not (home and dest):
            continue
        k = (loc, start.isoformat())
        cached = _drive.get(k)
        if not cached or time.time() - cached[0] > (120 if cfg.get("tomtom_key") else 900):
            _drive[k] = (time.time(), *drive_minutes(cfg, home, dest))
        _, mins, live = _drive[k]
        if mins < 3:                                  # basically next door — no banner
            continue
        leave = arrive - timedelta(minutes=mins + buffer)
        trips.append({"title": ev["title"], "start": arrive.isoformat(), "leave": leave.isoformat(),
                      "minutes": mins, "traffic": live})
    trips.sort(key=lambda t: t["leave"])
    if write_json("leave.json", {"trips": trips[:2]}):
        log("leave:", [(t["title"], t["leave"][11:16]) for t in trips[:2]] or "none")


# ── weekday-morning commute ────────────────────────────────────────────────
# config.json:
#   "commute": [{"name": "Pre-K", "to": "<address>", "school": true}, {"name": "Work", "to": "<address>"}],
#   "commute_hours": ["06:30", "09:30"]          (Monday–Friday)
# "school": true shows "No school" on days the calendar marks as a break/holiday.
#
# Optional chained trip with a leave-by time (drop-off on the way to work):
#   "morning_trip": {"name": "Spencer", "to_name": "SHQ", "to": "<work address>", "by": "08:45", "aim": "08:30",
#                    "via_name": "Pre-K", "via": "<school address>", "via_by": "08:00",
#                    "via_school": true, "stop_min": 5, "buffer_min": 0,
#                    "covers": ["Pre-K Dropoff"],       # calendar leave-by events this replaces
#                    "home_days": ["Wed"]}              # work from home: drop-off, then back home
# "morning_trip" can also be a list, one per person. Extra keys: "school": true (the
# destination is a school: "No school" on break days), "days": ["Mon", "Tue", ...].
# Leave time = the latest that still makes BOTH targets (work target always met; the
# drop-off target too, when traffic allows). Skips the stop on no-school days.
_commute = {}


def at_today(now, hm):
    h, m = map(int, hm.split(":"))
    return now.replace(hour=h, minute=m, second=0, microsecond=0)


def plan_trip(cfg, home, now, off_days, t=None, key="trip"):
    t = t or cfg["morning_trip"]
    if t.get("days") and now.strftime("%a") not in t["days"]:
        return None
    if t.get("school") and now.date().isoformat() in off_days:     # the destination itself is a school
        return {"name": t.get("name", ""), "to": t.get("to_name") or t["to"].split(",")[0], "off": True}
    via = t.get("via")
    skip = bool(via) and t.get("via_school", True) and now.date().isoformat() in off_days
    if now.strftime("%a") in (t.get("home_days") or []):
        # Work-from-home day: drop-off and back home. Only the drop-off time matters.
        if skip or not via or not t.get("via_by"):
            return None
        via_by = at_today(now, t["via_by"])
        if now > via_by:
            return None
        t = {**t, "to_name": "Home", "by": None}
        work, by = home, None
    else:
        by = at_today(now, t.get("by", "08:30"))
        if now > by:
            return None                                # already there (or gone): hide
        work = geocode(cfg, t["to"])
        if not work:
            raise ValueError("address not found: " + t["to"])
    stop = None
    if via and not skip:
        stop = geocode(cfg, via)
        if not stop:
            raise ValueError("address not found: " + via)
    pts = [home, stop, work] if stop else [home, work]
    dwell = int(t.get("stop_min", 5)) if stop else 0
    buf = int(t.get("buffer_min", 0))
    via_by = at_today(now, t["via_by"]) if stop and t.get("via_by") else None

    def leave_for(legs):
        lv = by - timedelta(minutes=sum(legs) + dwell + buf) if by else None
        if via_by:
            v = via_by - timedelta(minutes=legs[0])
            lv = min(lv, v) if lv else v
        return lv

    c = _commute.get(key)
    if not c or c[0] != (tuple(map(tuple, pts)), now.date()) or time.time() - c[1] > (300 if cfg.get("tomtom_key") else 1800):
        legs, live, free = drive_legs(cfg, pts)        # traffic right now: "if you leave now" times
        now_legs = legs
        leave = leave_for(legs)
        if leave > now + timedelta(minutes=10):        # re-ask with predicted traffic for that departure
            legs, live, free = drive_legs(cfg, pts, depart=leave)
            leave = leave_for(legs)
        _commute[key] = c = ((tuple(map(tuple, pts)), now.date()), time.time(), legs, live, free, now_legs)
    _, _, legs, live, free, now_legs = c
    leave = leave_for(legs)
    return {"name": t.get("name", ""), "to": t.get("to_name") or t["to"].split(",")[0],
            "by": by.isoformat(timespec="minutes") if by else None, "leave": leave.isoformat(timespec="minutes"),
            "via": (t.get("via_name") or via.split(",")[0]) if stop else None,
            "via_by": via_by.isoformat(timespec="minutes") if via_by else None,
            "skipped": (t.get("via_name") or "stop") if skip else None,
            "aim": at_today(now, t["aim"]).isoformat(timespec="minutes") if by and t.get("aim") else None,
            "legs": legs, "now_legs": now_legs, "stop_min": dwell, "minutes": sum(legs), "typical": free,
            "delay": max(0, sum(legs) - free), "live": live, "covers": t.get("covers") or []}


def in_commute_window(cfg, now):
    if now.weekday() > 4:
        return False
    a, b = (cfg.get("commute_hours") or ["06:30", "09:30"])[:2]
    hm = now.strftime("%H:%M")
    return a <= hm < b


def update_commute(cfg):
    dests = cfg.get("commute") or []
    now = datetime.now(TZ)
    if not (dests or cfg.get("morning_trip")) or not in_commute_window(cfg, now):
        write_json("commute.json", {"show": False})
        return
    home_q = cfg.get("home_address")
    if not home_q:
        write_json("commute.json", {"show": False, "error": "no home_address in config"})
        return
    home = geocode(cfg, home_q)
    if not home:
        write_json("commute.json", {"show": False, "error": "home address not found by the map service"})
        return
    off = no_school_days()
    today = now.date().isoformat()
    live = bool(cfg.get("tomtom_key"))
    out, err = [], None
    for d in dests:
        row = {"name": d.get("name") or d["to"].split(",")[0]}
        if d.get("school") and today in off:
            row["off"] = True
            out.append(row)
            continue
        try:
            dest = geocode(cfg, d["to"])
            if not (home and dest):
                raise ValueError("address not found: " + d["to"])
            k = d["to"]
            cached = _commute.get(k)
            if not cached or time.time() - cached[0] > (300 if live else 1800):   # live: every 5 min
                _commute[k] = (time.time(), *drive_route(cfg, home, dest))
            _, mins, is_live, free = _commute[k]
            row.update(minutes=mins, typical=free, delay=max(0, mins - free), live=is_live)
        except Exception as e:
            err = str(e)[:120]
        out.append(row)
    mt = cfg.get("morning_trip") or []
    trips = []
    for i, t in enumerate(mt if isinstance(mt, list) else [mt]):     # one trip, or one per person
        try:
            p = plan_trip(cfg, home, now, off, t, f"trip{i}")
            if p:
                trips.append(p)
        except Exception as e:
            err = str(e)[:120]
    live = live and not _tomtom["error"]
    write_json("commute.json", {"show": bool(out or trips), "live": live, "updated": now.isoformat(timespec="minutes"),
                                "trips": trips, "routes": out, "error": err or _tomtom["error"]})


# ── "Spencer is on his way home": ETA from his phone (OwnTracks app over Tailscale) ──
# The phone posts its location to /owntracks/<token> (exposed to his own devices only, via
# `tailscale serve`; set up by eta_setup.py). The location itself is kept in a private file,
# never in the dashboard's data folder; the screen only gets the ETA.
# config.json:
#   "eta": {"name": "Spencer", "token": "...", "work": "<work address>",
#           "hours": ["15:00", "21:00"], "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
#           "work_radius_m": 400, "home_radius_m": 250, "work_region": "Work"}
WHERE = os.path.join(os.path.dirname(CONFIG), "where.json")
_where_lock = threading.Lock()


def meters(a, b):
    from math import asin, cos, radians, sin, sqrt
    la1, lo1, la2, lo2 = map(radians, (a[0], a[1], b[0], b[1]))
    h = sin((la2 - la1) / 2) ** 2 + cos(la1) * cos(la2) * sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371000 * asin(sqrt(h))


def load_where():
    try:
        with open(WHERE) as f:
            return json.load(f)
    except Exception:
        return {}


def owntracks_post(cfg, msg):
    """One message from the OwnTracks app: a location fix or a region enter/leave."""
    e = cfg.get("eta") or {}
    kind = msg.get("_type")
    if kind not in ("location", "transition") or "lat" not in msg:
        return
    tst = int(msg.get("tst") or time.time())
    pt = [float(msg["lat"]), float(msg["lon"])]
    with _where_lock:
        w = load_where()
        today = datetime.fromtimestamp(tst, TZ).date().isoformat()
        if w.get("date") != today:
            w = {"date": today}
        if tst >= (w.get("fix") or {}).get("tst", 0):
            w["fix"] = {"lat": pt[0], "lon": pt[1], "tst": tst, "acc": msg.get("acc")}
        region = (e.get("work_region") or "Work").lower()
        work = geocode(cfg, e["work"]) if e.get("work") else None
        at_work = (work and meters(pt, work) <= int(e.get("work_radius_m", 400))) or \
                  region in [r.lower() for r in msg.get("inregions") or []]
        if kind == "transition" and (msg.get("desc") or "").lower() == region:
            at_work = msg.get("event") == "enter"
            if not at_work:
                w["left_work"] = tst
        if at_work:
            w["at_work"] = tst
        elif w.get("at_work") and w.get("left_work", 0) < w["at_work"]:
            w["left_work"] = tst                       # first fix away from work since being there
        os.makedirs(os.path.dirname(WHERE), exist_ok=True)
        tmp = WHERE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(w, f)
        os.chmod(tmp, 0o600)
        os.replace(tmp, WHERE)


_eta = {}


def update_eta(cfg):
    e = cfg.get("eta") or {}
    now = datetime.now(TZ)
    def hide(why=None):
        if write_json("eta.json", {"show": False, "why": why}) and _eta.get("shown"):
            log(f"eta: banner off ({why or 'outside hours'})")
            _eta["shown"] = False
    if not e.get("token"):
        return hide()
    if now.strftime("%a") not in (e.get("days") or ["Mon", "Tue", "Wed", "Thu", "Fri"]):
        return hide()
    a, b = (e.get("hours") or ["15:00", "21:00"])[:2]
    if not (a <= now.strftime("%H:%M") < b):
        return hide()
    w = load_where()
    fix = w.get("fix")
    if w.get("date") != now.date().isoformat() or not fix or not w.get("at_work"):
        return hide("not at work today")
    if w.get("left_work", 0) < w["at_work"] or fix["tst"] < w.get("left_work", 0):
        return hide("still at work")
    home = geocode(cfg, cfg.get("home_address", ""))
    if not home:
        return hide("home address not found")
    pt = [fix["lat"], fix["lon"]]
    if meters(pt, home) <= int(e.get("home_radius_m", 250)):
        return hide("home")
    if _eta.get("tst") != fix["tst"] or time.time() - _eta.get("at", 0) > 300:
        mins, live, free = drive_route(cfg, pt, home)
        _eta.update(tst=fix["tst"], at=time.time(), mins=mins, live=live, free=free)
    fixed = datetime.fromtimestamp(fix["tst"], TZ)
    eta = fixed + timedelta(minutes=_eta["mins"])
    if now > eta + timedelta(minutes=30):
        return hide("stopped somewhere")              # no news for a while: don't guess
    if not _eta.get("shown"):
        log(f"eta: banner on (left work {datetime.fromtimestamp(w['left_work'], TZ):%H:%M}, home ~{eta:%H:%M})")
        _eta["shown"] = True
    write_json("eta.json", {"show": True, "name": e.get("name", ""), "eta": eta.isoformat(timespec="minutes"),
                            "minutes": _eta["mins"], "fix": fixed.isoformat(timespec="minutes"),
                            "left": datetime.fromtimestamp(w["left_work"], TZ).isoformat(timespec="minutes"),
                            "delay": max(0, _eta["mins"] - _eta["free"]), "live": _eta["live"]})


# ── Google Keep: shared Family List + Olivia's quotes (see keep_source.py) ──
_quotes = {"keep": None}
_keep_fail = {"n": 0}


def keep_cfg(cfg):
    k = cfg.get("keep") or {}
    return k if k.get("email") and k.get("master_token") else None


def update_keep(cfg):
    k = keep_cfg(cfg)
    if not k:
        return
    import keep_source as ks
    try:
        keep = ks.client(k["email"], k["master_token"], os.path.join(DATA, "keep_state.json"))
        _keep_fail["n"] = 0
    except Exception as e:
        # Keep hiccups now and then; start a fresh session next minute and only
        # flag it on screen if it keeps failing (the list stays as last synced).
        ks._state["keep"] = None
        _keep_fail["n"] += 1
        why = f"{type(e).__name__}: {str(e)[:160]}"
        log(f"keep sync failed ({_keep_fail['n']}x): {why}")
        if _keep_fail["n"] >= 5:
            old = {}
            try:
                old = json.load(open(os.path.join(DATA, "tasks.json")))
            except Exception:
                pass
            bad_token = any(w in why for w in ("BadAuthentication", "NeedsBrowser", "LoginException"))
            write_json("tasks.json", {**old, "error": "Google Keep sign-in expired: run pi/keep_auth.py"
                                      if bad_token else "Google Keep not syncing (list may be out of date)"})
        return
    want = k.get("family_list") or "Family List"
    fam = ks.find_note(keep, want)
    if fam:
        items = ks.note_lines(fam, unchecked_only=True)
        if write_json("tasks.json", {"title": cfg.get("tasks_title") or fam.title, "items": items, "source": "keep"}):
            log(f"keep: {len(items)} open on '{fam.title}'")
    else:
        write_json("tasks.json", {"items": [], "error": f"Keep note '{want}' not found (is it shared with {k['email']}?)"})
    qn = ks.find_note(keep, k.get("quotes_note") or "Olivia")
    if qn:
        quotes = [q for q in (ks.clean_quote(l) for l in ks.note_lines(qn)) if q]
        if quotes:
            _quotes["keep"] = quotes
            write_json("quotes_keep.json", {"note": qn.title, "quotes": quotes})


def update_quote(cfg):
    import keep_source as ks
    quotes = _quotes["keep"]
    if not quotes and keep_cfg(cfg) and os.path.exists(os.path.join(DATA, "quotes_keep.json")):
        quotes = json.load(open(os.path.join(DATA, "quotes_keep.json"))).get("quotes")
    if keep_cfg(cfg) and not quotes:
        return                                     # wait for the first Keep sync (quote.html falls back meanwhile)
    js_quotes = ks.quotes_from_js(os.path.join(REPO, "quotes.js"))
    quotes = quotes or js_quotes
    if not quotes:
        return
    hp = os.path.join(DATA, "quote_history.json")
    if os.path.exists(hp):
        history = json.load(open(hp, encoding="utf-8"))
    else:                                          # everything in quotes.js has been on screen already
        history = {"seed": [ks.norm(q) for q in js_quotes], "days": {}}
    today = datetime.now(TZ).date()
    before = json.dumps(history, sort_keys=True)
    q = ks.pick_quote(quotes, history, today)
    if json.dumps(history, sort_keys=True) != before:
        with open(hp + ".tmp", "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=1)
        os.replace(hp + ".tmp", hp)
    if write_json("quote.json", {"date": today.isoformat(), "name": "Olivia", "quote": q,
                                 "source": "keep" if quotes is not js_quotes else "quotes.js"}):
        log("quote:", q)


# ── word of the day (never repeats; see wotd.py) ─────────────────────────────
def events_on(d):
    out = []
    for ev in _events:
        if ev.get("allDay"):
            s0 = date.fromisoformat(ev["start"])
            s1 = max(date.fromisoformat(ev.get("end") or ev["start"]), s0 + timedelta(days=1))
            if s0 <= d < s1:
                out.append(ev)
        elif datetime.fromisoformat(ev["start"]).astimezone(TZ).date() == d:
            out.append(ev)
    return out


def update_word(cfg):
    if not _cal["ready"]:                       # wait for today's calendar so activity days get themed words
        return
    import wotd
    today = datetime.now(TZ).date()
    titles = [ev["title"] for ev in events_on(today)]
    w = wotd.today_word(os.path.join(REPO, "words.json"), os.path.join(DATA, "wotd_history.json"), today, titles)
    if write_json("word.json", w):
        log("word:", w["word"][0], "/", w["label"], f"({w['words_left']} new left)")


# ── loops ───────────────────────────────────────────────────────────────────
def every(seconds, fn):
    def run():
        while True:
            try:
                fn(load_config())
            except Exception:
                log(f"{fn.__name__} error:\n" + traceback.format_exc(limit=2))
            time.sleep(seconds)
    threading.Thread(target=run, daemon=True).start()


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        p = urllib.parse.urlparse(path).path
        if p.startswith("/data/"):
            rel = os.path.normpath(urllib.parse.unquote(p[len("/data/"):])).lstrip("/")
            if rel.startswith(".."):
                return os.path.join(DATA, "missing")
            return os.path.join(DATA, rel)
        return super().translate_path(path)

    def end_headers(self):
        path = self.path.split("?")[0]
        if path.startswith("/data/") and path.endswith(".json"):
            self.send_header("Cache-Control", "no-store")
        elif path.endswith((".html", ".js", ".json", ".css")) or path.endswith("/"):
            self.send_header("Cache-Control", "no-cache")      # always check for updated pages after a pull
        super().end_headers()

    def log_message(self, *a):
        pass

    def do_POST(self):
        """OwnTracks: POST /owntracks/<token> (JSON). Answers [] as the app expects."""
        parts = [x for x in urllib.parse.urlparse(self.path).path.split("/") if x]
        token = (load_config().get("eta") or {}).get("token")
        if not token or parts != ["owntracks", token]:
            self.send_error(404)
            return
        try:
            n = min(int(self.headers.get("Content-Length") or 0), 100_000)
            msg = json.loads(self.rfile.read(n) or b"{}")
            for m in msg if isinstance(msg, list) else [msg]:
                owntracks_post(load_config(), m)
        except Exception as e:
            log("owntracks:", e)
        body = b"[]"
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    os.makedirs(PHOTOS, exist_ok=True)
    every(30, update_calendar)      # Google Calendar: ~30 s; iCal fallback throttles itself to 3 min
    every(15, update_tasks)         # family list: ~15 s
    every(5 * 60, update_photos)    # new photos in the Drive folder: ~5 min
    every(10 * 60, update_weather)  # weather: every 10 minutes
    every(60, update_alerts)        # severe weather: every minute
    every(60, update_leave)         # drive times: checked every minute, re-routed every 2 min (TomTom)
    every(60, update_keep)          # Google Keep (Family List + quotes), if set up
    every(60, update_quote)         # Olivia quote of the day: new quotes first
    every(60, update_word)          # word of the day: picked once a day, logged so it never repeats
    every(60, update_commute)       # weekday-morning commute: re-routed every 5 min (TomTom) / 30 min
    every(30, update_eta)           # on the way home: ETA from the phone's location, if set up
    every(60, update_air)           # air quality + pollen: refreshed every 30 minutes
    every(60, update_countdown)     # holiday / birthday / trip countdown: one a day
    every(60, update_note)          # weekly Pre-K note: 4-8 PM on the first two days of the week
    cfg = load_config()
    # "bind": "0.0.0.0" lets other machines on the home network load the dashboard (e.g. when
    # this server runs on mrpopp and the Pi only displays it). Default: this machine only.
    bind, port = cfg.get("bind", "127.0.0.1"), int(cfg.get("port", PORT))
    srv = ThreadingHTTPServer((bind, port), partial(Handler, directory=REPO))
    log(f"serving http://{'localhost' if bind == '127.0.0.1' else bind}:{port}/pi/dashboard.html")
    srv.serve_forever()


if __name__ == "__main__":
    sys.exit(main())
