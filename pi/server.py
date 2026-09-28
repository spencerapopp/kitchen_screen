#!/usr/bin/env python3
"""Kitchen dashboard server for the Raspberry Pi.

Serves the dashboard at http://localhost:8080/pi/dashboard.html and keeps three
small data files fresh in ~/kitchen-data (served at /data/):

  calendar.json  events from Google Calendar                    (every 30 seconds)
  tasks.json     open items on your Google Tasks family list   (every 15 seconds)
  photos.json    photos from the Google Drive "Kitchen Photos" folder, converted
                 to JPEG and resized, cached in ~/kitchen-data/photos/  (every 5 minutes)

Private settings (calendar addresses, Google sign-in) live only on the Pi in
~/.config/kitchen/config.json — never in the GitHub repo.
"""
import io
import json
import os
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
MAX_PHOTOS = 400


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


def window():
    today = datetime.now(TZ).date()
    start = today - timedelta(days=(today.weekday() + 1) % 7)       # Sunday of this week
    return start, start + timedelta(days=WEEKS * 7 + 1)


def calendar_from_api(cfg):
    start, end = window()
    cals = json.loads(gget(cfg, "https://www.googleapis.com/calendar/v3/users/me/calendarList?maxResults=250")).get("items", [])
    names = [n.lower() for n in (cfg.get("calendar_names") or [])]
    chosen = [c for c in cals if c.get("summary", "").lower() in names] or [c for c in cals if c.get("primary")]
    out = []
    t0 = datetime.combine(start, datetime.min.time(), TZ).isoformat()
    t1 = datetime.combine(end, datetime.min.time(), TZ).isoformat()
    for c in chosen:
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
                st, en = ev.get("start", {}), ev.get("end", {})
                if "dateTime" in st:
                    s = datetime.fromisoformat(st["dateTime"]).astimezone(TZ)
                    out.append({"title": title, "start": s.isoformat(), "allDay": False})
                elif "date" in st:
                    out.append({"title": title, "start": st["date"], "end": en.get("date") or st["date"], "allDay": True})
            if not r.get("nextPageToken"):
                break
            page = "&pageToken=" + r["nextPageToken"]
    return out, []


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
                    out.append({"title": title, "start": s.isoformat(), "allDay": False})
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
    # Same event on two calendars (e.g. shared family events) → show once.
    seen, unique = set(), []
    for ev in sorted(out, key=lambda x: x["start"]):
        k = (ev["title"].lower(), ev["start"])
        if k not in seen:
            seen.add(k)
            unique.append(ev)
    if errors and not unique:
        return log("calendar failed:", errors)          # keep the last good file
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
    write_json("photos.json", {"photos": keep, "error": f"{failed} photos could not be read" if failed else None})
    log(f"photos: {len(keep)} ({added} new)")


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
        if self.path.startswith("/data/") and self.path.split("?")[0].endswith(".json"):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass


def main():
    os.makedirs(PHOTOS, exist_ok=True)
    every(30, update_calendar)      # Google Calendar: ~30 s; iCal fallback throttles itself to 3 min
    every(15, update_tasks)         # family list: ~15 s
    every(5 * 60, update_photos)    # new photos in the Drive folder: ~5 min
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), partial(Handler, directory=REPO))
    log(f"serving http://localhost:{PORT}/pi/dashboard.html")
    srv.serve_forever()


if __name__ == "__main__":
    sys.exit(main())
