"""Google Keep for the kitchen screen: the shared Family List and Olivia's quotes.

Google has no Keep API for personal accounts, so this uses gkeepapi (unofficial, widely
used). It signs in as a dedicated Google account that your family notes are shared with,
using a long-lived "master token" saved in config.json by keep_auth.py.

config.json:
  "keep": {"email": "...", "master_token": "...",
           "family_list": "Family List",     # title of the shared list note
           "quotes_note": "Olivia"}           # title (or part of it) of the quotes note
"""
import json
import os
import re
import unicodedata

_state = {"keep": None, "email": None}


def norm(s):
    """Loose match key: lowercase letters and digits only."""
    s = unicodedata.normalize("NFKD", s).lower()
    return re.sub(r"[^a-z0-9]+", "", s)


def clean_quote(s):
    s = s.strip().lstrip("-•*·").strip()
    s = s.strip("\"'“”‘’").strip()
    return s


def client(email, master_token, state_path):
    """A synced gkeepapi.Keep, reusing saved state so each sync is small."""
    import gkeepapi
    k = _state["keep"]
    if k is None or _state["email"] != email:
        k = gkeepapi.Keep()
        state = None
        if os.path.exists(state_path):
            try:
                with open(state_path) as f:
                    state = json.load(f)
            except Exception:
                state = None
        try:
            k.authenticate(email, master_token, state=state, sync=True)
        except Exception:
            if state is None:
                raise
            k = gkeepapi.Keep()                       # saved state was stale: start clean
            k.authenticate(email, master_token, sync=True)
        _state.update(keep=k, email=email)
    else:
        k.sync()
    tmp = state_path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(k.dump(), f)
    os.replace(tmp, state_path)
    return k


def find_note(keep, title):
    """Best match by title: exact (case-insensitive) first, then 'contains'. Skips trashed notes."""
    want = (title or "").strip().lower()
    if not want:
        return None
    notes = [n for n in keep.all() if not n.trashed and (n.title or "").strip()]
    for n in notes:
        if n.title.strip().lower() == want:
            return n
    return next((n for n in notes if want in n.title.lower()), None)


def note_lines(note, unchecked_only=False):
    """Lines of a Keep note: list items, or text lines for a plain note."""
    if hasattr(note, "unchecked"):                     # a checklist
        items = note.unchecked if unchecked_only else note.items
        lines = [i.text for i in items]
    else:
        lines = (note.text or "").splitlines()
    return [l.strip() for l in lines if l.strip()]


# ── quote of the day: new quotes first, never the same one twice in a row of the cycle ──
def pick_quote(quotes, history, today):
    """quotes: list of strings. history: {"seed": [norm...], "days": {date: quote}}. Returns the quote."""
    key = today.isoformat()
    if key in history["days"] and norm(history["days"][key]) in {norm(q) for q in quotes}:
        return history["days"][key]
    shown = {}                                         # norm -> last date shown ("" for seed)
    for n in history.get("seed", []):
        shown[n] = ""
    for d, q in sorted(history["days"].items()):
        if d != key:
            shown[norm(q)] = d
    fresh = [q for q in quotes if norm(q) not in shown]
    if fresh:
        q = fresh[0]
    else:                                              # all shown: the one shown longest ago
        q = min(quotes, key=lambda x: shown.get(norm(x), ""))
    history["days"][key] = q
    return q


def quotes_from_js(path):
    """The fallback list in quotes.js (one quoted string per line)."""
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r'\s*"(.*)",?\s*$', line)
            if m:
                out.append(m.group(1).replace('\\"', '"'))
    return out
