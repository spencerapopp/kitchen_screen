# Kitchen screen

Pages shown inside the DAKboard kitchen display.

| Page | Where it shows | What it does |
|---|---|---|
| `card.html` | Bottom-right panel | Word of the day (changes at midnight) |
| `quote.html` | Caption along the bottom of the photo | One of Olivia's quotes (changes at midnight) |

## Everyday edits

- **Words:** `words.json`. The Pi picks one a day and never repeats a word (log: `~/kitchen-data/wotd_history.json`).
  Holiday words > activity words (party, swim, soccer, gymnastics, basketball, dentist, doctor) > the day's own word.
  Add new words to `"extra"`; the screen warns when fewer than 45 new words are left.
- **Olivia quotes:** from the shared Google Keep note (new quotes first), or `quotes.js` if Keep isn't set up.
- **Family list:** the shared Google Keep list if set up (`pi/keep_auth.py`), otherwise Google Tasks.
- **Health check on the Pi:** `python3 ~/kitchen_screen/pi/check.py`

The TV reloads these pages every few hours, so changes show up the same day.

## Calendar feed

`.github/workflows/calendar.yml` runs every two hours. It reads the calendars listed in the
`ICAL_URLS` secret (Settings → Secrets and variables → Actions; one secret iCal address per line)
and writes `events.json`.

This repo is public, so the only thing published is keywords for today's activities
(`swim`, `soccer`, …) — no titles, names, or times. The word card uses them to pick a themed word.

## Test a date

`card.html?date=2026-10-31`, `card.html?act=swim`, `quote.html?n=5`, `quote.html?solid`

## Raspberry Pi version (no DAKboard)

`pi/` runs the whole screen on the Pi: `pi/dashboard.html` (layout), `pi/server.py` (calendar,
Google Tasks, photos → `~/kitchen-data`), `pi/setup.sh` (one-command install),
`pi/immich_source.py` + `pi/immich_setup.py` (daily photo pick from Immich on mrpopp; without
it the photos come from the Drive "Kitchen Photos" folder),
`pi/google_auth.py` (one-time Google sign-in). Private settings stay on the Pi in
`~/.config/kitchen/config.json`. The Pi pulls this repo nightly at 3:30 AM.

Install on the Pi: `curl -fsSL https://raw.githubusercontent.com/spencerapopp/kitchen_screen/main/pi/setup.sh | bash`
