#!/usr/bin/env python3
"""Turn the kitchen Google TV on or off over Wi-Fi.

Same connection the Google Home app's remote uses (Android TV Remote, ports 6466/6467),
so it works even when Google Home routines can't reach the TV.

One-time pairing (a code appears on the TV):
    ~/kitchen_screen/pi/.venv/bin/python ~/kitchen_screen/pi/tv_power.py pair 192.168.4.XX
Then:
    tv_power.py off | on | status
Scheduled from crontab (see the guide).
"""
import asyncio
import json
import os
import sys
from datetime import datetime

from androidtvremote2 import AndroidTVRemote, CannotConnect, ConnectionClosed, InvalidAuth

DIR = os.path.expanduser("~/.config/kitchen")
CONF = os.path.join(DIR, "config.json")
CERT, KEY = os.path.join(DIR, "tv_cert.pem"), os.path.join(DIR, "tv_key.pem")


def log(msg):
    print(msg)
    with open(os.path.join(DIR, "kiosk.log"), "a") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} tv {msg}\n")


def load():
    with open(CONF) as f:
        return json.load(f)


def save_host(host):
    cfg = load()
    cfg["tv_host"] = host
    with open(CONF, "w") as f:
        json.dump(cfg, f, indent=2)
    os.chmod(CONF, 0o600)


async def pair(host):
    save_host(host)
    tv = AndroidTVRemote("Kitchen Pi", CERT, KEY, host)
    await tv.async_generate_cert_if_missing()
    await tv.async_start_pairing()
    code = input("Type the code shown on the TV: ").strip()
    await tv.async_finish_pairing(code)
    log(f"paired with {host}")


async def power(want):
    host = load().get("tv_host")
    if not host:
        sys.exit("Pair first:  tv_power.py pair <TV IP address>")
    tv = AndroidTVRemote("Kitchen Pi", CERT, KEY, host)
    await tv.async_generate_cert_if_missing()
    for attempt in range(4):                      # the TV's Wi-Fi can be slow to answer from standby
        try:
            await tv.async_connect()
            break
        except InvalidAuth:
            sys.exit("The TV forgot this Pi. Pair again:  tv_power.py pair " + host)
        except (CannotConnect, ConnectionClosed) as e:
            if attempt == 3:
                log(f"can't reach the TV at {host}: {e}")
                sys.exit(1)
            await asyncio.sleep(10)
    for _ in range(30):                           # power state arrives just after connecting
        if tv.is_on is not None:
            break
        await asyncio.sleep(0.1)
    on = tv.is_on
    if want == "status":
        print("on" if on else "off" if on is False else "unknown")
    elif (want == "on") == bool(on) and on is not None:
        print(f"Already {want}.")
    else:
        # SLEEP/WAKEUP only ever go one way (POWER toggles, so it's only a fallback below).
        tv.send_key_command("SLEEP" if want == "off" else "WAKEUP")
        await asyncio.sleep(5)
        if tv.is_on is not None and tv.is_on != (want == "on"):
            tv.send_key_command("POWER")          # some TVs ignore SLEEP/WAKEUP
            await asyncio.sleep(2)
        log(f"turned {want} (TV reports {'on' if tv.is_on else 'off' if tv.is_on is False else 'unknown'})")
    tv.disconnect()


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "pair" and len(sys.argv) == 3:
        asyncio.run(pair(sys.argv[2]))
    elif cmd in ("on", "off", "status"):
        asyncio.run(power(cmd))
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
