#!/usr/bin/env bash
# Opens the dashboard full-screen and reopens it if the browser ever closes.
# Started automatically at login (see setup.sh).
exec 9>/tmp/kitchen-kiosk.lock
flock -n 9 || exit 0                      # already running

URL="http://localhost:8080/pi/dashboard.html"
CHROME=$(command -v chromium-browser || command -v chromium)
unclutter -idle 1 >/dev/null 2>&1 &       # hide the mouse pointer

# wait for the dashboard server
for _ in $(seq 60); do curl -fs "$URL" >/dev/null && break; sleep 2; done

while true; do
  "$CHROME" --kiosk --noerrdialogs --disable-infobars --disable-session-crashed-bubble \
    --no-first-run --password-store=basic --check-for-update-interval=31536000 \
    --autoplay-policy=no-user-gesture-required --user-data-dir="$HOME/.config/kitchen/chromium" \
    --app="$URL" --class=kiosk-dashboard >/dev/null 2>&1
  sleep 3
done
