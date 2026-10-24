# Running the server

## Services

| Service | Port | Notes |
| --- | --- | --- |
| web-server | 54993 | Sign-in (`/login`), sign-up (`/signup`), health check (`/healthz`) |
| lobby-server | 54994 | Lobby; Blowfish-encrypted traffic |
| world-server | 54992 | Session routing, groups |
| map-server | 1989 | The game |

Configs are in `configs/*.toml` (`web`, `lobby`, `world`, `map`, `servers`). All four services
share one SQLite database, `data/garlemald.db`.

## Starting and restarting

`scripts/run-all.sh`:
- builds the workspace (release by default);
- starts all four services;
- wires the map server's console to a named pipe at `logs/map-server.gm.fifo`.

Our launcher starts it automatically when the server is localhost and not answering. By hand:

```sh
nohup ./scripts/run-all.sh > ~/Library/Logs/XIVLegacy/server.log 2>&1 &
```

**Restarting:**
- Stop `run-all.sh` and the four `target/release/*` processes, then start it again.
- The map server is ready once `/healthz` answers and its log shows `zone-load battle npc spawn
  pass complete`, about 3 minutes with the open-world monsters.
- Restarting logs every player out, and **clears `logs/map-server.log`**. Copy it first if you
  need it. Packet logs in `logs/packet-logs/` survive.

**Database migrations:**
- Seed files in `common/sql/seed/*.sql` are bundled into the binaries and applied once each,
  recorded in `schema_migrations`.
- The web, lobby and world servers share the database, so whichever service starts first applies
  a new seed.
- Editing a seed that's already applied has no effect: apply it by hand or add a new file.
- Back up first: `sqlite3 data/garlemald.db ".backup data/backup.db"`.

## Reloading Lua scripts

Scripts in `scripts/lua/` are cached. `reload` on the console drops the cache, so the next use
re-reads the file. A coroutine that's already running (a tutorial in progress) keeps its old code.

## The console

Write one command per line to the pipe:

```sh
echo "givegil 10000 Firstname Lastname" > logs/map-server.gm.fifo
```

Results appear in `logs/map-server.log` as `command result response=...`.

| Command | Use |
| --- | --- |
| `help`, `who`, `version`, `reload` | Info; reload Lua scripts |
| `warp <zone> <x> <y> <z> <name>` | Move a player |
| `setseq <quest_id> <sequence> <name>` | Set a quest's sequence |
| `talkto <actor_class_id> <name>` | Run an NPC's talk hook for a player, server-side only (the client gets no event context) |
| `pushtrigger <actor_class_id> <name>` | Same for a push trigger |
| `givegil <qty> <name>`, `giveexp <qty> <class_id> <name>` | Grants |
| `revive <name>`, `die <name>`, `home <name>`, `sethome <aetheryte_id> <name>` | Life and homepoint |
| `speed <multiplier> [name]` | Movement speed |
| `issuechocobo <appearance> <chocobo_name> <name>`, `rentchocobo <minutes> <name>`, `dismount <name>` | Chocobos |
| `joingc <gc> <name>`, `setgcrank <gc> <rank> <name>`, `addgcseals <gc> <amount> <name>` | Grand Companies |
| `hireretainer`, `dismissretainer`, `listretainers` | Retainers |
| `setsleeping`, `dream`, `wake`, `accruerest` | Inn and rest |

In-game GM chat commands (`!endevent`, `!setjob`, `!warp`, …) are Lua scripts in
`scripts/lua/commands/gm/`. The console doesn't run them. Type them in chat instead. `!endevent`
closes a stuck event.

## Logs worth knowing

| Line | Meaning |
| --- | --- |
| `RX EventStart (inbound, pre-dispatch) session=… owner=… event_name=…` | The client started an event |
| `TX 0x0130 RunEventFunction … function=…` / `TX 0x0131 EndEvent` | The server drove or closed it |
| `fire_signal: draining parked coroutines signal=… resumed=N` | A script signal; `resumed=0` means nothing was waiting |
| `game ticker heartbeat … parked_time=… parked_signal=… parked_event=…` | Every 10 s: how many coroutines wait on each kind of thing |
| `auto-attack engage rejected — not in active mode` | The player clicked an enemy without drawing (F) |
| `swing ready but skipped … distance=… attack_range=…` | Locked on but out of range |
| `battle: auto-attack resolved … defender_hp=…` | A hit |
| `content battle complete` | Every enemy in a content fight is dead |
| `zone-in bundle dispatched` / `zone-in-complete` | Zone-in started / finished on the client |
