# World monsters

> **Approximate, not retail-exact.** A believable first population built from the best surviving
> sources. Stats are assumed and many positions are camp-level estimates. Treat the numbers as
> placeholders to replace as better data turns up; the generator makes that a re-run.

Out of the box the server had no open-world monsters:
- 51 battle-NPC spawn points, almost all tutorial or quest content;
- and the boot spawn pass never created battle NPCs anyway.

We added **3,193 monsters in 463 groups** across the 19 field zones of La Noscea, Coerthas, the
Black Shroud and Thanalan. This is upstream pull request
[swstegall/Garlemald-Server#216](https://github.com/swstegall/Garlemald-Server/pull/216).

## Sources

All of these are via the XIVLegacy Dev Team's
[xivl-captures](https://github.com/XIVLegacy/xivl-captures) research data (CC BY 4.0):

1. **Exact positions:** about 160 monsters decoded from retail 1.23b packet captures, mostly in
   the Central and North Shroud.
2. **Mooglebox regional camp maps (2012):** about 250 camps, each with a monster name, level range,
   approximate count and map coordinates.
3. **Gamer Escape 1.x monster pages:** zone, map coordinates, level and behavior. These also give
   the join from monster name to client actor class.
4. **Retail level and HP pairs** from captures.

## Map coordinates to world coordinates

1.x maps use one coordinate grid per region:

```
world_x = 100 × map_x + x_offset
world_z = 100 × map_y + z_offset
```

| Region | x offset | z offset | Fitted against |
| --- | --- | --- | --- |
| La Noscea | −2473 | −2945 | 25 NPCs with known world positions |
| Coerthas | −3263 | −1259 | A captured antelope; checked against the 5 camp aetherytes |
| Black Shroud | −3043 | −3752 | 10 NPCs and 3 camp aetherytes |
| Thanalan | −2640 | −3044 | An Eastern Thanalan NPC; checked against a captured Lead Coblyn |

The median error is about 20 world units. City maps (inside Ul'dah, for example) use their own
small grids and don't follow this.

## Ground height

The server has no terrain or navmesh data. Each monster's y is blended from the nearest known
positions in its zone:
- captures, NPC seeds and gathering points;
- player positions parsed out of our own packet logs.

Monsters far from any sample can float or sink. Real terrain heights would have to come from the
client's zone data.

## Stats

- **HP** follows the retail curve (median per level, log-linear between): 80 at level 1, about 175
  at 10, 410 at 20, 750 at 30.
  - Gamer Escape's HP column mixes level brackets (a level-1 Star Marmot listed at 720), so it
    isn't used.
- **Attack, defense and the rest** use the server's existing level-scaled fallbacks.
- **Aggression** comes from the camp maps and Gamer Escape behavior flags.
- **Respawn** is 90 seconds.

## Class paths

132 monster actor classes the server had without a `classPath` got one from the client's own
monster scripts. An empty class path crashes the client on spawn. The client's script folder names
are obscured with a letter substitution (see the client docs), and there are 804 monster scripts.

Monster classes without a server-side base init script get the standard monster init values. All
the shipped `*Standard` monster scripts return the same tuple. That fix is
[#213](https://github.com/swstegall/Garlemald-Server/pull/213).

## The generator and the boot pass

- `tools/world_spawns/generate.py` writes `common/sql/seed/101_world_monster_spawns.sql`.
  - Run it against a database the seed hasn't been applied to, so the class path repairs are
    kept.
  - Source copies and attribution are in `tools/world_spawns/data/`.
- At boot, `PacketProcessor::spawn_zone_load_battle_npcs` spawns every group with `spawnType = 0`
  outside private areas, through the same path as `SpawnBattleNpcById`.
- **Actor numbers** start at `0x20000` per zone. Bit `0x40000` marks content-instance actors.
- **Idle cost:** about 5% CPU on the map server with all 3,193 spawned.

## What's skipped

About 380 entries, where no client actor class with an appearance row was found: snurbles,
phurbles, hippocerfs, several Ixali, bandits.

## Dungeon monsters

The four 1.0 dungeons had no monsters at all. Seed `130_dungeon_monsters.sql` adds **456 monsters
in 42 groups**. Nothing spawns with the zone: every run is a copy of its own (see
[Dungeon copies](#dungeon-copies)), and its monsters spawn into that copy.

| Dungeon | Zone | Monsters | Levels |
| --- | --- | --- | --- |
| The Thousand Maws of Toto-Rak | 159 | 138 | 35–39 |
| Dzemael Darkhold | 231 | 140 | 52 |
| The Aurum Vale | 245 | 91 | 52–56 |
| Cutter's Cry | 246 | 87 | 50–56 |

### Where the positions come from

Caladius shared placement sheets with us, from a project that never got started: for each spawn, a map id, the
monster's name and a pixel on that map. The client's own map sheet turns pixels into world
positions:

- `data/01/03/05/12.DAT` has 72-byte rows of 18 int32. Fields 3 and 4 are the map's x and z
  offsets, field 5 its scale (pixels per yalm), field 6 the map id. Row ids come from the
  (first, count) pairs in `01/03/05/13.DAT`.
- `pixel = (world + offset) × scale`, so `world = pixel / scale − offset`. Z points south, the same
  way as the map's y.
- Every dungeon map is 2560×2048 pixels at scale 2 (half a yalm per pixel). Field maps use scale 1;
  other small maps use 4 or 8.
- `data/01/03/03/61.DAT` maps a map id to its texture group. The map is 80 tiles, files
  `0xGGGG0000` to `0xGGGG004F`, 10 wide, each a 256×256 DXT1 GTEX.

| Map | Dungeon | x offset | z offset |
| --- | --- | --- | --- |
| 1161, 1163, 1165, 1167 | Cutter's Cry | 1792, 1824, 1952, 2080 | 2144, 2112, 2272, 2368 |
| 1241 | Toto-Rak | −544 | −224 |
| 1321, 1331 | Dzemael Darkhold, upper and lower | 560, 736 | 384, 593 |
| 1341, 1343, 1345 | The Aurum Vale | 1328, 1648, 1488 | −768, −800, −1072 |

Drawn back onto the decoded maps, every known door and barrier, and every spawn, lands in a
corridor or room. Each spawn has to use its own map's offsets: a dungeon's floors differ.

The same sheet covers every map in the game, so it can also replace the fitted region offsets
above.

### Heights, levels and classes

- **Heights** were read in the test client: one probe per cluster of spawns within 4 yalms.
- **Levels and aggression** come from Gamer Escape's 1.x pages. A few kinds missing there take
  the level of a like kind in the same dungeon. HP carries the curve above on: 1825 × 1.0577^(level − 40), so about 1,400 at 35 and 4,500 at 56.
- **Classes, names and looks** are the client's own dungeon entries (the 32xxxxx and 33xxxxx
  name ids), all `*Standard` monster scripts.
- **Left out:** nine Dzemael spawns the sheet names only "Unknown", and two Aurum Vale Imperial
  Hoplomachus spots whose height could not be read.
- **Not retail yet:** bosses, chests, the doors and their gimmicks, the time limit and the party
  size are still to do. The dungeons' barrier and door actors spawn with the open zone, so they
  don't show inside a copy. Still to do as well are the Aurum Vale's
  hazards: its yellow goldbile pools give a brief poison-like effect (possibly Bio), its gas
  rooms inflict Gold Lung, and its first boss stacks an effect that at three or more stacks you
  had to clear by grabbing a special remedy.

Cutter's Cry had an empty zone row (no zone name or class). The map sheet gives it area 415 in
region 104, following Nanawa (412, `wil0Dungeon02`) and Copperbell (414, `wil0Dungeon04`), so the
seed names it `wil0Dungeon05`.

### Dungeon copies

Each run is a copy of the dungeon for a party or a solo player. Two parties in Toto-Rak at once
each see only their own monsters, and party members inside one copy see each other.

- **Entering:** `!dungeon <totorak|dzemael|aurum|cutters>` (GM level 2 by default). It runs
  `scripts/lua/dungeon.lua`, which creates the copy in the dungeon's zone, spawns the dungeon's
  monsters into it, and brings in the typer's party members who are in the same zone. Retail
  queued players through NPCs by each entrance (Toto-Rak's was Bloisirant in the South Shroud);
  those aren't scripted yet.
- **Leaving:** `!dungeon leave` puts you at the nearest camp's aetherial gate. Logging out
  inside also leaves. The copy goes on with whoever is still inside, and it ends with the last
  one out.
- **Directors:** the client's own for each dungeon, `InstanceRaid/InstanceRaidAurumVale`,
  `InstanceRaid/InstanceRaidCuttersCry`, `Occupancy/RaidFst0Dungeon03` (Toto-Rak) and
  `Occupancy/RaidRoc0Dungeon01` (Dzemael).

How copies work in the map server (`content_instance.rs`):

- A copy gets a unique id and one of 32 slots in its zone. The slot is folded into its actors'
  numbers, so two copies never share an actor id. Content scripts' battle npc ids must stay
  under 4096 for that.
- Every actor and player carries its copy's id in the zone core, and "who is near me" only pairs
  actors of the same copy. That one check keeps streaming, broadcasts, chat, aggro and area
  attacks inside the copy. The open zone is copy 0.
- `DoZoneChangeContentParty` brings the party along; `DoZoneChangeContent` stays solo, which is
  what quest duties use. The content's hooks run once, on the owner's session.
- `player:LeaveContent()`: a member just leaves. The owner hands the copy to a member still
  inside, or the copy ends.
