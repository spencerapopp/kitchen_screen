#!/usr/bin/env bash
# Kitchen dashboard installer for Raspberry Pi OS (desktop).
# Run on the Pi:
#   curl -fsSL https://raw.githubusercontent.com/spencerapopp/kitchen_screen/main/pi/setup.sh | bash
# Safe to run again — it updates what's there.
set -euo pipefail

REPO_URL="https://github.com/spencerapopp/kitchen_screen.git"
DIR="$HOME/kitchen_screen"
CONF="$HOME/.config/kitchen/config.json"
say() { printf '\n\033[1;34m== %s\033[0m\n' "$*"; }

say "Installing packages"
sudo apt-get update -qq
sudo apt-get install -y -qq git python3-venv unclutter fonts-roboto fonts-noto-cjk >/dev/null
CHROME=$(command -v chromium-browser || command -v chromium || true)
if [ -z "$CHROME" ]; then sudo apt-get install -y -qq chromium >/dev/null || sudo apt-get install -y -qq chromium-browser >/dev/null; fi
CHROME=$(command -v chromium-browser || command -v chromium)

say "Getting the dashboard code"
if [ -d "$DIR/.git" ]; then git -C "$DIR" pull -q --ff-only; else git clone -q "$REPO_URL" "$DIR"; fi

say "Setting up Python"
python3 -m venv "$DIR/pi/.venv"
"$DIR/pi/.venv/bin/pip" install -q --upgrade pip
"$DIR/pi/.venv/bin/pip" install -q icalendar recurring-ical-events pillow pillow-heif

say "Settings"
mkdir -p "$(dirname "$CONF")"
if [ ! -f "$CONF" ]; then
  cat > "$CONF" <<'JSON'
{
  "ical_urls": [],
  "tasks_list": "",
  "tasks_title": "Family list",
  "calendar_names": ["Family"],
  "home_address": "",
  "tomtom_key": "",
  "leave_buffer_min": 5,
  "leave_titles": ["Pre-K Dropoff"],
  "arrive_early": {"Pre-K Dropoff": 5},
  "places": {
    "Custer Parkway Preschool II": "2129 Teakwood Ln, Plano, TX 75075"
  },
  "photos_folder_id": "1qkg2u_GU_Qlrz5jlsbEaANxPN0MUJORg"
}
JSON
  chmod 600 "$CONF"
fi
if [ "$("$DIR/pi/.venv/bin/python" -c "import json;print(len(json.load(open('$CONF'))['ical_urls']))")" = "0" ]; then
  echo "Paste your calendar's 'Secret address in iCal format' (Google Calendar → Settings → your calendar)."
  echo "One per line. Press Enter on an empty line when done."
  URLS=()
  while IFS= read -r line </dev/tty; do [ -z "$line" ] && break; URLS+=("$line"); done
  "$DIR/pi/.venv/bin/python" - "$CONF" "${URLS[@]}" <<'PY'
import json, sys
path, urls = sys.argv[1], [u.strip() for u in sys.argv[2:] if u.strip()]
cfg = json.load(open(path)); cfg["ical_urls"] = urls
json.dump(cfg, open(path, "w"), indent=2)
print(f"Saved {len(urls)} calendar(s).")
PY
fi

if [ -z "$("$DIR/pi/.venv/bin/python" -c "import json;print(json.load(open('$CONF')).get('home_address',''))")" ]; then
  echo
  echo "Home address, for 'leave by' drive times (stays on this Pi). Press Enter to skip:"
  IFS= read -r HOME_ADDR </dev/tty || true
  "$DIR/pi/.venv/bin/python" - "$CONF" "$HOME_ADDR" <<'PY'
import json, sys
path, addr = sys.argv[1], sys.argv[2].strip()
cfg = json.load(open(path)); cfg["home_address"] = addr
cfg.setdefault("tomtom_key", ""); cfg.setdefault("leave_buffer_min", 5)
json.dump(cfg, open(path, "w"), indent=2)
PY
fi

say "Starting the dashboard server (runs at boot)"
mkdir -p "$HOME/.config/systemd/user"
cat > "$HOME/.config/systemd/user/kitchen.service" <<EOF
[Unit]
Description=Kitchen dashboard server
After=network-online.target

[Service]
ExecStart=$DIR/pi/.venv/bin/python $DIR/pi/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF
sudo loginctl enable-linger "$USER"
systemctl --user daemon-reload
systemctl --user enable --now kitchen.service
systemctl --user restart kitchen.service

say "Full-screen browser at login"
chmod +x "$DIR/pi/kiosk.sh"
mkdir -p "$HOME/.config/autostart"
cat > "$HOME/.config/autostart/kitchen.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Kitchen dashboard
Exec=$DIR/pi/kiosk.sh
X-GNOME-Autostart-enabled=true
EOF
# labwc (the default desktop on newer Pi OS) reads its own autostart file too
if [ -d /etc/xdg/labwc ] || command -v labwc >/dev/null; then
  mkdir -p "$HOME/.config/labwc"
  touch "$HOME/.config/labwc/autostart"
  # A user autostart file replaces the system one, so pull the system one back in (panel, desktop).
  if [ -f /etc/xdg/labwc/autostart ] && ! grep -q /etc/xdg/labwc/autostart "$HOME/.config/labwc/autostart"; then
    sed -i '1i . /etc/xdg/labwc/autostart' "$HOME/.config/labwc/autostart"
  fi
  grep -q kiosk.sh "$HOME/.config/labwc/autostart" || echo "$DIR/pi/kiosk.sh &" >> "$HOME/.config/labwc/autostart"
fi

say "Keeping the screen awake"
sudo raspi-config nonint do_blanking 1 || true

say "Nightly update at 3:30 AM"
( crontab -l 2>/dev/null | grep -v kitchen_screen || true ; \
  echo "30 3 * * * git -C $DIR pull -q --ff-only && XDG_RUNTIME_DIR=/run/user/$(id -u) systemctl --user restart kitchen.service && pkill -f 'kitchen/chromium' ; true" ) | crontab -

say "Done"
echo "Dashboard: http://localhost:8080/pi/dashboard.html"
echo "Next: connect Google (family list + photos) — Claude will give you the command."
echo "Reboot to start full-screen mode:  sudo reboot"
