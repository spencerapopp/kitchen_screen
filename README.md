# Kitchen screen

Pages shown inside the DAKboard kitchen display.

| Page | Where it shows | What it does |
|---|---|---|
| `card.html` | Bottom-right panel | Word of the day for 45 seconds, then one of Olivia's quotes for 15 seconds |
| `header.html` | Top strip, between the clock and the weather | Next two countdowns, today's sunset, tonight's moon |

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

This repo is public, so only two things are published:

- keywords for today's activities (`swim`, `soccer`, …), with no titles or times
- the title and date of upcoming events whose title contains **birthday** or **#countdown**

To count down to anything else, add `#countdown` to the event title in Google Calendar.

## Test a date

`card.html?date=2026-10-31&slide=word`, `card.html?date=2026-09-29&act=swim`, `card.html?slide=quote`,
`header.html?date=2026-12-20`
