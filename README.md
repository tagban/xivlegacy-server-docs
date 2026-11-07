# XIVLegacy server documentation

How we run [Garlemald](https://github.com/swstegall/Garlemald-Server), the Rust FINAL FANTASY XIV
1.23b server emulator, for the XIVLegacy native client: setup and operations, how events and
quests work inside it, the open-world monster data we added, every fix we made and contributed,
class test results and known gaps.

**Community:** questions, testing and news on the [XIVLegacy Discord](https://discord.gg/D9k3khqvy8).

**A passion project.** XIVLegacy preserves FINAL FANTASY XIV as it was in 1.0 so people can walk through it again — and seeing the original up close may help explain why Square Enix rebuilt it as *A Realm Reborn*. If you enjoy old Eorzea, please play the game today: FINAL FANTASY XIV has a [free trial](https://freetrial.finalfantasyxiv.com/) with no time limit.

**Player reference:** items, quests, monsters, NPCs and leves of 1.23b at the [XIVLegacy Reference](https://tagban.github.io/xivlegacy-reference/).

Our fork is [tagban/Garlemald-Server](https://github.com/tagban/Garlemald-Server). Client-side
notes (protocol, opcodes, client behavior) live in
[xivlegacy-client-docs](https://github.com/tagban/xivlegacy-client-docs).

> Not affiliated with Square Enix. FINAL FANTASY XIV is a registered trademark of Square Enix Holdings Co., Ltd.

## Server status

**Live status:** [tagban.github.io/xivlegacy-server-docs](https://tagban.github.io/xivlegacy-server-docs/): is `xiv.ffxi.cc` up, who's online, uptime and the last 7 days.

The [server-status workflow](.github/workflows/server-status.yml) runs every 30 minutes from GitHub. It runs
[`tools/server_status.py`](tools/server_status.py), which checks the server from outside (its public `/status` page on 54993 and the
lobby and world ports). Then it:

- publishes the [status page](status-page/index.html) and its `status.json` / `history.json` on GitHub Pages
  (30 days of history are kept on the `status-data` branch, so `main` gets no commit per run);
- posts to Discord when the `DISCORD_WEBHOOK_URL` secret is set (a channel webhook): a roll call of who's online,
  every run while someone is on, and a message when the server goes down or comes back;
- feeds the [status box](status-page/moghouse-widget.html) for moghouse.cc or any site: paste it into a WordPress "Custom HTML" block.

Run it by hand from the Actions tab (**Server status**, Run workflow).

## Contents

| Page | What it covers |
| --- | --- |
| [Running the server](docs/running.md) | Services and ports, starting and restarting, the database, logs, the GM console |
| [Events and quests](docs/events-and-quests.md) | Event dispatch, the coroutine scheduler and signals, quest hooks, directors, the opening tutorials, quest duties |
| [World monsters](docs/world-monsters.md) | Open-world spawns: sources, coordinate conversion, HP, the generator, the boot pass; dungeon monsters and dungeon copies |
| [NPC and quest placement](docs/npc-placements.md) | How quest NPCs, triggers and fights are placed and given heights; coordinate frames, sources, pitfalls; the generated [placement data](docs/npc-placements-data.md) |
| [Fixes and contributions](docs/fixes.md) | Every fix, with its cause, the upstream pull request or local commit |
| [Test results](docs/test-results.md) | The per-class matrix from driving the real client |
| [Known gaps](docs/known-gaps.md) | What's missing or approximate |
