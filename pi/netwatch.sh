#!/bin/bash
# kitchen-netwatch: gets the kitchen Pi back online by itself.
#
# Installed by pi/netwatch_setup.sh as /usr/local/sbin/kitchen-netwatch and run every 2 minutes
# by a systemd timer (as root). What it does when the internet is unreachable:
#   10 min offline  -> restart NetworkManager (the fix that worked on Nov 3, 2026)
#   20 min offline  -> reboot, but only if the router itself is unreachable too, and at most
#                      once every 6 hours. If the router answers but the internet doesn't, the
#                      whole house is offline (Frontier/eero), so a reboot wouldn't help: it waits.
# State lives in /run (RAM), so it doesn't wear the SD card. The only disk write is a
# timestamp when it reboots. Everything it does goes to the journal:
#   journalctl -t kitchen-netwatch
set -u

STATE=${STATE:-/run/kitchen-netwatch}
STAMP=${STAMP:-/var/lib/kitchen-netwatch/last_reboot}
RESTART_AFTER=${RESTART_AFTER:-600}     # seconds offline before restarting NetworkManager
REBOOT_AFTER=${REBOOT_AFTER:-1200}      # seconds offline before rebooting
REBOOT_GAP=${REBOOT_GAP:-21600}         # at most one reboot per 6 hours
NOW=${NOW:-$(date +%s)}
UPTIME=${UPTIME:-$(cut -d. -f1 /proc/uptime)}

log() { logger -t kitchen-netwatch "$*" 2>/dev/null; echo "$*"; }
gateway() { ip route show default 2>/dev/null | awk '/^default/ {print $3; exit}'; }

online() {
    ping -c1 -W3 1.1.1.1 >/dev/null 2>&1 || ping -c1 -W3 8.8.8.8 >/dev/null 2>&1 || return 1
    getent ahostsv4 github.com >/dev/null 2>&1 || getent ahostsv4 google.com >/dev/null 2>&1   # DNS too
}

router_ok() {
    local gw; gw=$(gateway)
    [ -n "$gw" ] && ping -c1 -W3 "$gw" >/dev/null 2>&1
}

mkdir -p "$STATE"

if online; then
    if [ -f "$STATE/down_since" ]; then
        log "back online after $(( (NOW - $(cat "$STATE/down_since")) / 60 )) min"
    fi
    rm -f "$STATE"/*
    exit 0
fi

[ "$UPTIME" -lt 300 ] && exit 0                     # just booted: give Wi-Fi a few minutes

if [ ! -f "$STATE/down_since" ]; then
    echo "$NOW" > "$STATE/down_since"
    gw=$(gateway)
    if [ -n "$gw" ]; then log "offline (router $gw)"; else log "offline (no route to the router)"; fi
    exit 0
fi

off=$(( NOW - $(cat "$STATE/down_since") ))

if [ ! -f "$STATE/restarted" ]; then
    if [ "$off" -ge "$RESTART_AFTER" ]; then
        log "offline $(( off / 60 )) min: restarting NetworkManager"
        echo "$NOW" > "$STATE/restarted"
        systemctl restart NetworkManager
    fi
    exit 0
fi

[ "$off" -lt "$REBOOT_AFTER" ] && exit 0

if router_ok; then
    [ -f "$STATE/house_noted" ] || { log "router answers but the internet doesn't: whole-house outage, not rebooting"; touch "$STATE/house_noted"; }
    exit 0
fi

last=$(cat "$STAMP" 2>/dev/null || echo 0)
if [ $(( NOW - last )) -lt "$REBOOT_GAP" ]; then
    [ -f "$STATE/gap_noted" ] || { log "still offline, but already rebooted $(( (NOW - last) / 60 )) min ago: waiting"; touch "$STATE/gap_noted"; }
    exit 0
fi

log "offline $(( off / 60 )) min and the router is unreachable after a NetworkManager restart: rebooting"
mkdir -p "$(dirname "$STAMP")" && echo "$NOW" > "$STAMP"
sync
systemctl reboot
