#!/usr/bin/env python3
"""Check the XIVLegacy server and publish its status.

Run by .github/workflows/server-status.yml every 30 minutes. Standard library only.

  python3 tools/server_status.py --data DIR --site DIR

DIR (--data) is the checkout of the `status-data` branch: it keeps history.json and
state.json between runs. --site is where status.json and history.json are written for the
status page (GitHub Pages) and the moghouse.cc status box.

Discord: set DISCORD_WEBHOOK_URL (a channel webhook) to post
  - a roll call of who's online, every run while someone is on (like the FFXI bridge),
  - a message when the server goes down or comes back.
Without it, nothing is posted.
"""

import argparse
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

HOST = os.environ.get("XIV_HOST", "xiv.ffxi.cc")
STATUS_URL = os.environ.get("XIV_STATUS_URL", f"http://{HOST}:54993/status")
PORTS = {"web": 54993, "lobby": 54994, "world": 54992}
KEEP_DAYS = 30
TRIES = 3
WAIT = 20  # seconds between tries, so a restart in progress isn't reported as down
UA = "xivlegacy-status-check (+https://github.com/tagban/xivlegacy-server-docs)"


def now():
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def port_open(port, timeout=8):
    try:
        with socket.create_connection((HOST, port), timeout=timeout):
            return True
    except OSError:
        return False


def fetch_status():
    req = urllib.request.Request(STATUS_URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)


def check():
    """One check, retried: (up, status json or None, services dict, error text)."""
    err = ""
    for attempt in range(TRIES):
        services = {name: port_open(port) for name, port in PORTS.items()}
        status = None
        try:
            status = fetch_status()
        except (urllib.error.URLError, OSError, ValueError) as e:
            err = f"status page: {e}"
        if status is not None and all(services.values()):
            return True, status, services, ""
        if status is not None:
            err = "no answer on " + ", ".join(f"{n} ({PORTS[n]})" for n, ok in services.items() if not ok)
        if attempt < TRIES - 1:
            time.sleep(WAIT)
    return False, status, services, err


def load(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def save(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def uptime(history, since):
    pts = [h for h in history if parse(h["t"]) >= since]
    if not pts:
        return None
    return round(100 * sum(1 for h in pts if h["up"]) / len(pts), 1)


def post_discord(text):
    url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if not url:
        print("discord: no DISCORD_WEBHOOK_URL, not posting:", text.splitlines()[0], file=sys.stderr)
        return
    body = json.dumps({"content": text, "allowed_mentions": {"parse": []}}).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json", "User-Agent": UA}
    )
    try:
        urllib.request.urlopen(req, timeout=15).read()
        print("discord: posted", text.splitlines()[0], file=sys.stderr)
    except urllib.error.URLError as e:
        # A Discord hiccup must not fail the job (the status page still updates).
        print("discord: post failed:", e, file=sys.stderr)


def ago(delta):
    m = int(delta.total_seconds() // 60)
    if m < 60:
        return f"{m} min"
    h, m = divmod(m, 60)
    if h < 48:
        return f"{h} h {m} min" if m else f"{h} h"
    return f"{h // 24} days"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--site", required=True)
    args = ap.parse_args()
    os.makedirs(args.data, exist_ok=True)
    os.makedirs(args.site, exist_ok=True)

    t = now()
    up, status, services, err = check()
    status = status or {}
    count = int(status.get("players_online") or 0) if up else 0
    online = [
        {"name": r.get("name", "?"), "city": r.get("city", "")}
        for r in status.get("recent", [])
        if r.get("online")
    ] if up else []

    hist_path = os.path.join(args.data, "history.json")
    state_path = os.path.join(args.data, "state.json")
    history = load(hist_path, [])
    state = load(state_path, {})
    world = status.get("world") or state.get("world") or "XIVLegacy"

    history.append({"t": iso(t), "up": up, "players": count})
    cutoff = t - timedelta(days=KEEP_DAYS)
    history = [h for h in history if parse(h["t"]) >= cutoff]

    was_up = state.get("up")
    since = state.get("since") or iso(t)
    if was_up is None or was_up != up:
        since = iso(t)
    peak_today = max([h["players"] for h in history if h["t"][:10] == iso(t)[:10]] or [0])

    # Discord: state changes first, then the roll call.
    if was_up is not None and was_up != up:
        if up:
            down_for = ago(t - parse(state.get("since", iso(t))))
            post_discord(f"🟢 **{world}** is back up (down for about {down_for}).")
        else:
            post_discord(
                f"🔴 **{world}** is down: {err or 'no answer'}. "
                f"Checked from outside at {t.strftime('%H:%M')} UTC."
            )
    if up and count > 0:
        names = ", ".join(
            f"{p['name']} ({p['city']})" if p["city"] else p["name"] for p in online
        )
        others = count - len(online)
        if others > 0:
            names = (names + f" and {others} more") if names else f"{others} players"
        post_discord(f"👥 **Online on {world} ({count}):** {names}")

    state = {
        "up": up,
        "since": since,
        "checked": iso(t),
        "world": world,
        "last_error": err if not up else "",
    }
    public = {
        "checked": iso(t),
        "up": up,
        "since": since,
        "world": world,
        "host": HOST,
        "players_online": count,
        "online": online,
        "services": services,
        "error": err if not up else "",
        "peak_today": peak_today,
        "uptime_24h": uptime(history, t - timedelta(hours=24)),
        "uptime_7d": uptime(history, t - timedelta(days=7)),
        "uptime_30d": uptime(history, cutoff),
    }
    save(hist_path, history)
    save(state_path, state)
    save(os.path.join(args.site, "status.json"), public)
    save(os.path.join(args.site, "history.json"), history)
    print(json.dumps(public, ensure_ascii=False))


if __name__ == "__main__":
    main()
