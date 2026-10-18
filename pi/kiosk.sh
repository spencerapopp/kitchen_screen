#!/usr/bin/env bash
# Opens the dashboard full-screen and reopens it if the browser ever closes.
# Started automatically at login (see setup.sh).
exec 9>/tmp/kitchen-kiosk.lock
flock -n 9 || exit 0                      # already running

LOCAL="http://localhost:8080/pi/dashboard.html"
# "dashboard_url" in config.json points the screen at another server (e.g. mrpopp);
# if that server doesn't answer within 2 minutes, the Pi's own server is used instead.
URL=$(python3 -c "import json,os;print(json.load(open(os.path.expanduser('~/.config/kitchen/config.json'))).get('dashboard_url',''))" 2>/dev/null)
URL=${URL:-$LOCAL}
CHROME=$(command -v chromium-browser || command -v chromium)
command -v unclutter >/dev/null && [ -n "$DISPLAY" ] && unclutter -idle 1 >/dev/null 2>&1 &   # hide the pointer (X11 only)
exec >>"$HOME/.config/kitchen/kiosk.log" 2>&1
echo "$(date) kiosk starting"

# wait for the dashboard server
for _ in $(seq 60); do curl -fs "$URL" >/dev/null && break; sleep 2; done
if [ "$URL" != "$LOCAL" ] && ! curl -fs "$URL" >/dev/null; then echo "$(date) $URL not answering, using $LOCAL"; URL=$LOCAL; fi

while true; do
  "$CHROME" --kiosk --noerrdialogs --disable-infobars --disable-session-crashed-bubble \
    --no-first-run --password-store=basic --check-for-update-interval=31536000 \
    --autoplay-policy=no-user-gesture-required --user-data-dir="$HOME/.config/kitchen/chromium" \
    --app="$URL" --class=kiosk-dashboard
  sleep 3
done
