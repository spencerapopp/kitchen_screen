#!/usr/bin/env bash
# Turn the Pi's HDMI picture off or on. With no signal, the TV goes to sleep by itself
# (TCL: "No signal power off"); Google Home or the remote wakes it in the morning.
#   display.sh off | on | status
# Scheduled from crontab, e.g.  30 21 * * * ~/kitchen_screen/pi/display.sh off
set -u
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
if [ -z "${WAYLAND_DISPLAY:-}" ]; then                       # cron/SSH: find the desktop session
  sock=$(ls "$XDG_RUNTIME_DIR"/wayland-[0-9] 2>/dev/null | head -1)
  export WAYLAND_DISPLAY="${sock##*/}"
fi
OUT="${KITCHEN_OUTPUT:-HDMI-A-1}"
log() { echo "$(date '+%F %T') display $*" >> "$HOME/.config/kitchen/kiosk.log"; }

if ! command -v wlr-randr >/dev/null; then
  echo "wlr-randr is missing. Install it with:  sudo apt install -y wlr-randr"; exit 1
fi

case "${1:-status}" in
  off)
    wlr-randr --output "$OUT" --off && log off && echo "Picture off." ;;
  on)
    wlr-randr --output "$OUT" --on
    sleep 2
    wlr-randr --output "$OUT" --mode 1920x1080 2>/dev/null   # back to full HD
    sleep 2
    pkill -f 'kitchen/chromium'                              # reopen the dashboard full-screen
    log on && echo "Picture on." ;;
  status)
    wlr-randr ;;
  *)
    echo "usage: $0 off|on|status"; exit 2 ;;
esac
