"""Kitchen-screen photos from Immich (the family photo server on mrpopp).

Once a day the screen picks a fresh set of about 500 photos from every Immich account
listed in config.json, then keeps screen-sized copies in ~/kitchen-data/photos/:

  pinned        everything in an Immich album called "Kitchen Screen" (any account)
  on this day   photos taken around today's date in past years
  recent        the last couple of months
  favorites     hearted photos
  people        photos with named faces (Explore > People in Immich)
  every year    the rest, spread evenly across the years

Only photos with people in them are picked automatically (set "people_only": false to allow
any photo); the Kitchen Screen album and favorites are shown as they are. Put a photo in an
album called "Hide from Kitchen" to keep it off the screen for good.

Skipped: videos, archived/hidden/locked photos, screenshots and other phone-shaped
images, tiny images, and the same photo appearing in two accounts.

config.json:
  "immich": {
    "url": "http://192.168.4.54:2283",
    "keys": {"Spencer": "<API key>", "Cookie": "<API key>"},
    "count": 500,                       optional
    "album": "Kitchen Screen",          optional
    "people": ["Olivia"],               optional; default = every named person
    "recent_days": 60,                  optional
    "captions": true                    optional; "On this day · 2019", "Oct 2021 · Dallas"
  }
API keys need these permissions: asset.read, asset.view, album.read, person.read
(plus face.read so photos crop around faces; without it the crop uses a rule of thumb).
Set it up with:  python3 ~/kitchen_screen/pi/immich_setup.py
"""
import json
import os
import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone

FIRST_YEAR = 2000
SKIP_NAME = re.compile(r"screen.?shot|screen.?record|screencap|scan[_ -]|receipt", re.I)
BASE = {"type": {"eq": "IMAGE"}, "visibility": {"eq": "timeline"}}
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
_retry = {"at": 0, "error": None}
_not_ready = set()                                # asset ids with no Immich preview yet (cleared each new pick)
PICK_RULES = 2
_faces_off = set()                                # accounts whose key lacks face.read


class Immich:
    def __init__(self, url, key, who, timeout=30):
        self.url, self.key, self.who, self.timeout = url.rstrip("/"), key, who, timeout
        self.extra = {}                              # filters added to every search (e.g. the hide album)

    def call(self, method, path, body=None, raw=False):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.url + "/api" + path, data=data, method=method, headers={
            "x-api-key": self.key, "Accept": "application/octet-stream" if raw else "application/json",
            **({"Content-Type": "application/json"} if data else {})})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            out = r.read()
        return out if raw else json.loads(out or b"null")

    def random(self, size, **flt):
        return self.call("POST", "/search/random", {"filter": {**BASE, **self.extra, **flt}, "size": size,
                                                     "withExif": True}) or []

    def search(self, size, **flt):
        r = self.call("POST", "/search/metadata", {"filter": {**BASE, **self.extra, **flt}, "size": size,
                                                    "withExif": True})
        return ((r or {}).get("assets") or {}).get("items") or []

    def thumbnail(self, asset_id):
        return self.call("GET", f"/assets/{asset_id}/thumbnail?size=preview", raw=True)


def iso(d):
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def taken(a):
    s = a.get("localDateTime") or a.get("fileCreatedAt") or ""
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def usable(a, pinned=False):
    if a.get("type") not in (None, "IMAGE") or a.get("isTrashed") or a.get("isArchived"):
        return False
    if a.get("visibility") not in (None, "timeline"):
        return False
    if a.get("resized") is False:                 # Immich hasn't made its screen-size copy yet
        return False
    if pinned:                                    # you put it in the album on purpose: show it
        return True
    if SKIP_NAME.search(a.get("originalFileName") or ""):
        return False
    ex = a.get("exifInfo") or {}
    w, h = a.get("width") or ex.get("exifImageWidth"), a.get("height") or ex.get("exifImageHeight")
    if w and h:
        if min(w, h) < 500:
            return False
        if max(w, h) / min(w, h) > 2.05:           # phone-screen shapes: screenshots, receipts, long scans
            return False
    return True


def focal_point(api, asset_id, jpg):
    """Where to keep in frame when the photo is cropped to fill the panel: [x, y] as fractions.
    Uses Immich's face boxes when the key has face.read; otherwise a phone-photo rule of thumb
    (people sit in the upper part of portrait shots)."""
    if api and api.who not in _faces_off:
        try:
            faces = api.call("GET", f"/faces?id={asset_id}") or []
            boxes = [(f["boundingBoxX1"] / f["imageWidth"], f["boundingBoxY1"] / f["imageHeight"],
                      f["boundingBoxX2"] / f["imageWidth"], f["boundingBoxY2"] / f["imageHeight"])
                     for f in faces if f.get("imageWidth") and f.get("imageHeight")]
            if boxes:
                x1, y1 = min(b[0] for b in boxes), min(b[1] for b in boxes)
                x2, y2 = max(b[2] for b in boxes), max(b[3] for b in boxes)
                return [round((x1 + x2) / 2, 3), round((y1 + y2) / 2, 3)]
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                _faces_off.add(api.who)              # this key lacks face.read: stop asking
        except Exception:
            pass
    try:
        from PIL import Image
        import io
        w, h = Image.open(io.BytesIO(jpg)).size
    except Exception:
        return None
    return [0.5, 0.35] if h > w else [0.5, 0.45]


def caption(a, bucket, today):
    t = taken(a)
    if not t:
        return ""
    if bucket == "on this day" and t.year < today.year:
        return f"On this day · {t.year}"
    city = ((a.get("exifInfo") or {}).get("city") or "").strip()
    return f"{MONTHS[t.month - 1]} {t.year}" + (f" · {city}" if city else "")


def gather(api, cfg, today, log):
    """Candidate photos from one account, grouped by why they'd be shown.

    Only photos with people in them are picked automatically ("people_only", on by default),
    so DIY shots of light fixtures, wiring, receipts and the like stay off the screen. The
    "Kitchen Screen" album and favorites are trusted as they are. Anything in an album called
    "Hide from Kitchen" never shows."""
    out = {k: [] for k in ("pinned", "on this day", "recent", "favorites", "people", "years", "backup")}
    album = (cfg.get("album") or "Kitchen Screen").strip().lower()
    hide = (cfg.get("hide_album") or "Hide from Kitchen").strip().lower()
    try:
        albums = api.call("GET", "/albums") or []
        name = lambda x: (x.get("albumName") or "").strip().lower()
        hide_ids = [x["id"] for x in albums if name(x) == hide]
        if hide_ids:
            api.extra = {"albumIds": {"none": hide_ids}}
        ids = [x["id"] for x in albums if name(x) == album]
        if ids:
            out["pinned"] = api.search(1000, albumIds={"any": ids})
    except urllib.error.HTTPError as e:
        log(f"immich {api.who}: albums skipped ({e.code})")
    with_people = {"hasPeople": {"eq": True}} if cfg.get("people_only", True) else {}
    for y in range(FIRST_YEAR, today.year):
        try:
            day = today.replace(year=y)
        except ValueError:                          # Feb 29 in a non-leap year
            day = date(y, 2, 28)
        out["on this day"] += api.random(6, takenAt={"gte": iso(day - timedelta(days=2)),
                                                     "lt": iso(day + timedelta(days=3))}, **with_people)
    days = int(cfg.get("recent_days", 60))
    out["recent"] = api.random(150, takenAt={"gte": iso(today - timedelta(days=days))}, **with_people)
    out["favorites"] = api.random(200, isFavorite={"eq": True})
    try:
        want = {n.strip().lower() for n in cfg.get("people") or []}
        ppl = api.call("GET", "/people?withHidden=false&size=1000") or {}
        pids = [p["id"] for p in ppl.get("people") or []
                if (p.get("name") or "").strip() and (not want or p["name"].strip().lower() in want)]
        if pids:
            out["people"] = api.random(250, personIds={"any": pids[:100]})
    except urllib.error.HTTPError as e:
        log(f"immich {api.who}: people skipped ({e.code})")
    for y in range(FIRST_YEAR, today.year + 1):
        out["years"] += api.random(25, takenAt={"gte": iso(date(y, 1, 1)), "lt": iso(date(y + 1, 1, 1))}, **with_people)
    if with_people and sum(len(v) for k, v in out.items() if k != "pinned") < 300:
        # Face detection hasn't covered the library yet: keep the screen full with any photos.
        out["backup"] = api.random(400)
    return out


def choose(pools, count, today, rng=random):
    """pools: [(who, {bucket: [assets]})]. Returns [{id, who, caption}] of about `count` photos."""
    quota = {"pinned": 150, "on this day": int(count * .12), "recent": int(count * .2),
             "favorites": int(count * .2), "people": int(count * .24)}
    picked, seen = [], set()

    def take(a, who, bucket):
        if not usable(a, pinned=bucket == "pinned"):
            return False
        keys = {a.get("id"), a.get("checksum"), (a.get("originalFileName"), a.get("localDateTime"))} - {None}
        if keys & seen:
            return False
        seen.update(keys)
        picked.append({"id": a["id"], "who": who, "bucket": bucket, "caption": caption(a, bucket, today)})
        return True

    for bucket, cap in quota.items():
        items = [(who, a) for who, p in pools for a in p.get(bucket) or []]
        rng.shuffle(items)
        n = 0
        for who, a in items:
            if n >= cap or len(picked) >= count:
                break
            n += take(a, who, bucket)
    # Fill the rest round-robin by year so no year is left out.
    by_year = {}
    for who, p in pools:
        for a in p.get("years") or []:
            t = taken(a)
            by_year.setdefault(t.year if t else 0, []).append((who, a))
    for lst in by_year.values():
        rng.shuffle(lst)
    while len(picked) < count and any(by_year.values()):
        for y in sorted(by_year):
            if by_year[y] and len(picked) < count:
                who, a = by_year[y].pop()
                take(a, who, "years")
    floor = min(count, 200)                          # only when people-photos run short
    backup = [(who, a) for who, p in pools for a in p.get("backup") or []]
    rng.shuffle(backup)
    for who, a in backup:
        if len(picked) >= floor:
            break
        take(a, who, "backup")
    rng.shuffle(picked)
    return picked


def update(cfg, *, data_dir, photos_dir, write_json, to_jpeg, log, now=None):
    im = cfg["immich"]
    url = im.get("url") or "http://192.168.4.54:2283"
    keys = im.get("keys") or {}
    if isinstance(keys, list):
        keys = {f"account {i + 1}": k for i, k in enumerate(keys)}
    apis = {who: Immich(url, k, who) for who, k in keys.items() if k}
    seconds = int(cfg.get("photo_seconds", 20))
    if not apis:
        write_json("photos.json", {"photos": [], "error": "Immich: no API keys in config.json"})
        return
    today = (now or datetime.now()).date()
    pick_file = os.path.join(data_dir, "immich_pick.json")
    sig = json.dumps({k: v for k, v in im.items() if k != "keys"}, sort_keys=True) + "|" + ",".join(sorted(apis)) \
        + f"|v{PICK_RULES}"                          # new pick rules take effect the moment the code updates
    try:
        pick = json.load(open(pick_file))
    except (OSError, ValueError):
        pick = {}

    error = None
    stale = pick.get("date") != today.isoformat() or pick.get("sig") != sig
    if stale and pick.get("items") and time.time() < _retry["at"]:
        error = _retry["error"]                       # mrpopp was down a moment ago; don't hammer it
    elif stale:
        pools, failed = [], []
        for who, api in apis.items():
            try:
                pools.append((who, gather(api, im, today, log)))
            except urllib.error.HTTPError as e:
                failed.append(f"{who} ({'API key rejected' if e.code in (401, 403) else e.code})")
            except Exception as e:
                failed.append(f"{who} (can't reach mrpopp: {type(e).__name__})")
        if pools:
            _not_ready.clear()
            items = choose(pools, int(im.get("count", 500)), today)
            pick = {"date": today.isoformat(), "sig": sig, "items": items}
            with open(pick_file + ".tmp", "w") as f:
                json.dump(pick, f)
            os.replace(pick_file + ".tmp", pick_file)
            counts = {}
            for x in items:
                counts[x["bucket"]] = counts.get(x["bucket"], 0) + 1
            log(f"immich pick: {len(items)} photos " + ", ".join(f"{k} {v}" for k, v in counts.items()))
        if failed:
            error = "Immich: " + ", ".join(failed) + (" (showing the last set)" if pick.get("items") else "")
            _retry.update(at=time.time() + 30 * 60, error=error)
            log("immich:", error)

    os.makedirs(photos_dir, exist_ok=True)
    focus_file = os.path.join(data_dir, "immich_focus.json")
    try:
        focus = json.load(open(focus_file))
    except (OSError, ValueError):
        focus = {}
    keep, captions, focal, added, broken, not_ready = [], [], [], 0, 0, 0
    for x in pick.get("items") or []:
        name = f"im_{x['id']}.jpg"
        path = os.path.join(photos_dir, name)
        if not os.path.exists(path):
            api = apis.get(x["who"])
            if not api or added >= 200 or x["id"] in _not_ready:   # spread big first downloads over a few runs
                continue
            try:
                jpg = to_jpeg(api.thumbnail(x["id"]))
                with open(path + ".tmp", "wb") as f:
                    f.write(jpg)
                os.replace(path + ".tmp", path)
                added += 1
                focus[x["id"]] = focal_point(api, x["id"], jpg)
            except urllib.error.HTTPError as e:
                if e.code == 404:                     # no preview in Immich yet: skip it today, quietly
                    _not_ready.add(x["id"])
                    not_ready += 1
                else:
                    broken += 1
                    if broken <= 3:
                        log("immich photo failed:", x["id"], e)
                continue
            except Exception as e:
                broken += 1
                if broken <= 3:
                    log("immich photo failed:", x["id"], type(e).__name__, e)
                continue
        keep.append("photos/" + name)
        captions.append((x.get("caption") or "") if im.get("captions", True) else "")
        if x["id"] not in focus:                      # photos cached before focal points existed
            try:
                focus[x["id"]] = focal_point(apis.get(x["who"]), x["id"], open(path, "rb").read())
            except Exception:
                focus[x["id"]] = None
        focal.append(focus.get(x["id"]))
    if pick.get("items"):
        wanted = {os.path.basename(k) for k in keep}
        for f in os.listdir(photos_dir):
            if f.endswith(".jpg") and f not in wanted and (f.startswith("im_") or keep):
                os.remove(os.path.join(photos_dir, f))
        ids = {x["id"] for x in pick["items"]}
        focus = {k: v for k, v in focus.items() if k in ids}
    with open(focus_file + ".tmp", "w") as f:
        json.dump(focus, f)
    os.replace(focus_file + ".tmp", focus_file)
    if not_ready:
        log(f"immich: {not_ready} photos skipped today (Immich has no preview for them yet)")
    # The screen only shows a problem the family would notice: no photos, or a set that's
    # gone stale because mrpopp has been unreachable since before today. Details: check.py / logs.
    detail = error or (f"{broken} photos failed to download" if broken else None)
    if keep and pick.get("date") == today.isoformat():
        error = None
    if not keep and not error:
        error = "Immich: no photos available yet"
    write_json("photos.json", {"photos": keep, "captions": captions, "focus": focal, "seconds": seconds,
                                "source": "immich", "error": error, "detail": detail})
    if added:
        log(f"photos: {len(keep)} from Immich ({added} new)")
