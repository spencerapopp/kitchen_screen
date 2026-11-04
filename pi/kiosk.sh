#!/usr/bin/env bash
# Opens the dashboard full-screen and reopens it if the browser ever closes.
# Started automatically at login (see setup.sh).
exec 9>/tmp/kitchen-kiosk.lock
flock -n 9 || exit 0                      # already running

LOCAL="http://localhost:8080/pi/dashboard.html"
# "dashboard_url" in config.json points the screen at the main server (mrpopp). The Pi's own
# server keeps running as a standby with its own fresh data:
#   - mrpopp stops answering for ~1 minute  -> the screen switches to the Pi's server
#   - mrpopp answers again for 5 minutes    -> the screen switches back
REMOTE=$(python3 -c "import json,os;print(json.load(open(os.path.expanduser('~/.config/kitchen/config.json'))).get('dashboard_url',''))" 2>/dev/null)
CHROME=$(command -v chromium-browser || command -v chromium)
command -v unclutter >/dev/null && [ -n "$DISPLAY" ] && unclutter -idle 1 >/dev/null 2>&1 &   # hide the pointer (X11 only)
exec >>"$HOME/.config/kitchen/kiosk.log" 2>&1
echo "$(date) kiosk starting${REMOTE:+ (main server: $REMOTE)}"

up() { curl -fs --max-time 5 "$1" >/dev/null; }

# wait (up to 2 min) for a server: the main one if set, else the Pi's own
for _ in $(seq 60); do
  { [ -n "$REMOTE" ] && up "$REMOTE"; } && break
  [ -z "$REMOTE" ] && up "$LOCAL" && break
  sleep 2
done

stay_local=0                                  # set after a failover: wait for 5 healthy minutes first
while true; do
  if [ -n "$REMOTE" ] && [ "$stay_local" = 0 ] && up "$REMOTE"; then URL=$REMOTE; else URL=$LOCAL; fi
  [ "$URL" = "$LOCAL" ] && [ -n "$REMOTE" ] && echo "$(date) showing the Pi's own dashboard (standby)"
  [ "$URL" = "$REMOTE" ] && echo "$(date) showing the dashboard from $REMOTE"
  "$CHROME" --kiosk --noerrdialogs --disable-infobars --disable-session-crashed-bubble \
    --no-first-run --password-store=basic --check-for-update-interval=31536000 \
    --autoplay-policy=no-user-gesture-required --user-data-dir="$HOME/.config/kitchen/chromium" \
    --app="$URL" --class=kiosk-dashboard &
  pid=$!
  bad=0; good=0
  while kill -0 "$pid" 2>/dev/null; do
    sleep "${CHECK_EVERY:-20}"
    [ -z "$REMOTE" ] && continue
    if up "$REMOTE"; then bad=0; good=$((good + 1)); else good=0; bad=$((bad + 1)); fi
    if [ "$URL" = "$REMOTE" ] && [ "$bad" -ge 3 ]; then             # ~1 min down: fail over
      echo "$(date) $REMOTE stopped answering: switching to the Pi's own server"
      stay_local=1; kill "$pid"; break
    fi
    if [ "$URL" = "$LOCAL" ] && [ "$good" -ge 15 ]; then            # 5 min healthy: go back
      echo "$(date) $REMOTE is back: switching to it"
      stay_local=0; kill "$pid"; break
    fi
  done
  wait "$pid" 2>/dev/null
  sleep 3
done
