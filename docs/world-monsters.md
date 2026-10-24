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
