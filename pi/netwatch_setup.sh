#!/bin/bash
# Installs (or updates) the network watchdog. Run on the Pi:
#   sudo bash ~/kitchen_screen/pi/netwatch_setup.sh
# Remove it:
#   sudo bash ~/kitchen_screen/pi/netwatch_setup.sh --remove
#
# The script is copied to /usr/local/sbin (owned by root), so the nightly git pull never
# changes what runs as root. After pulling a new version, run this again to update it.
set -e
[ "$(id -u)" -eq 0 ] || { echo "Run with sudo:  sudo bash $0"; exit 1; }
DIR=$(cd "$(dirname "$0")" && pwd)

if [ "${1:-}" = "--remove" ]; then
    systemctl disable --now kitchen-netwatch.timer 2>/dev/null || true
    rm -f /etc/systemd/system/kitchen-netwatch.{service,timer} /usr/local/sbin/kitchen-netwatch
    systemctl daemon-reload
    echo "Network watchdog removed."
    exit 0
fi

install -o root -g root -m 0755 "$DIR/netwatch.sh" /usr/local/sbin/kitchen-netwatch

cat > /etc/systemd/system/kitchen-netwatch.service <<'EOF'
[Unit]
Description=Kitchen screen: bring the network back if it drops
After=NetworkManager.service

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/kitchen-netwatch
EOF

cat > /etc/systemd/system/kitchen-netwatch.timer <<'EOF'
[Unit]
Description=Kitchen screen: check the internet every 2 minutes

[Timer]
OnBootSec=3min
OnUnitActiveSec=2min
AccuracySec=15s

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable --now kitchen-netwatch.timer
systemctl start kitchen-netwatch.service
echo
echo "Network watchdog installed. It checks every 2 minutes:"
echo "  10 min offline -> restarts Wi-Fi (NetworkManager)"
echo "  20 min offline and the router unreachable -> reboots (max once per 6 hours)"
echo "See what it has done:  journalctl -t kitchen-netwatch --no-pager"
echo "Right now: $(/usr/local/sbin/kitchen-netwatch >/dev/null; [ -f /run/kitchen-netwatch/down_since ] && echo offline || echo online)"
