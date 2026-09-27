# Kitchen screen

Pages shown inside the DAKboard kitchen display.

| Page | Where it shows | What it does |
|---|---|---|
| `card.html` | Bottom-right panel | Word of the day (changes at midnight) |
| `quote.html` | Caption along the bottom of the photo | One of Olivia's quotes (changes at midnight) |

## Everyday edits

- **Change a word:** edit its line in `words.js`. Each month lists one word per day, in order.
- **Add an Olivia quote:** add a line to `quotes.js`.
- **Holiday words:** `WOTD.MOVING` in `words.js` (Lunar New Year, Mid-Autumn, Thanksgiving, Mother's Day, Father's Day).
- **Activity words:** `WOTD.ACTIVITY` in `words.js` — used on days the calendar has swim, soccer, basketball, a birthday, the dentist, or the doctor.

The TV reloads these pages every few hours, so changes show up the same day.

## Calendar feed

`.github/workflows/calendar.yml` runs every two hours. It reads the calendars listed in the
`ICAL_URLS` secret (Settings → Secrets and variables → Actions; one secret iCal address per line)
and writes `events.json`.

This repo is public, so the only thing published is keywords for today's activities
(`swim`, `soccer`, …) — no titles, names, or times. The word card uses them to pick a themed word.

## Test a date

`card.html?date=2026-10-31`, `card.html?act=swim`, `quote.html?n=5`, `quote.html?solid`
