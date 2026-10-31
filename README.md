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

## Contents

| Page | What it covers |
| --- | --- |
| [Running the server](docs/running.md) | Services and ports, starting and restarting, the database, logs, the GM console |
| [Events and quests](docs/events-and-quests.md) | Event dispatch, the coroutine scheduler and signals, quest hooks, directors, the opening tutorials |
| [World monsters](docs/world-monsters.md) | Open-world spawns: sources, coordinate conversion, HP, the generator, the boot pass; dungeon monsters and dungeon copies |
| [Fixes and contributions](docs/fixes.md) | Every fix, with its cause, the upstream pull request or local commit |
| [Test results](docs/test-results.md) | The per-class matrix from driving the real client |
| [Known gaps](docs/known-gaps.md) | What's missing or approximate |
