# NPC and quest placement

How we decide where quest NPCs, event triggers and quest fights stand, and how we get their
heights right. The server has no terrain or navmesh data, so every y in a seed is a number someone
found. The full list is on [NPC placement data](npc-placements-data.md):
- every spawn our seeds add;
- every one a later seed moved, with its height change;
- the fights the quests spawn.

That page is generated from the seeds, so regenerate it rather than editing it (see
[Regenerating the data page](#regenerating-the-data-page)).

## Coordinates

- **World units.** x runs east, y up and z south. Rotation is in radians: 0 faces south (+z),
  and π/2 (1.57) faces east.
- **Facing a point.** An NPC faces (dx, dz) with rotation `atan2(dx, dz)`.
- **Counter staff.** Staff on an east wall face west at −1.57.
- **One space per zone.** A town's "a" zone (206 Gridania, 209 Ul'dah, 230 Limsa Lominsa) shares
  the town's world coordinates. Private areas (`privateAreaName`/`privateAreaLevel`) are
  instances laid over the same space, so a spawn in a private area uses the zone's own
  coordinates.

## Where positions come from

These are the sources we use, most reliable first.

1. **Cutscene files.** The scene files under `client/cut/<name>/<name>` hold the cast's float
   triples. Field cutscenes (`*_fld*`) are in world coordinates, so an actor's spot can be read
   straight out. This is how most Grand Company duty spots and Urianger's camps were placed.
2. **Town cutscenes need an offset.** Scenes shot in town maps (`*_twn*`) use the town's own
   frame:
   - **Ul'dah:** world = local + (−88, 186, 142). The Ossuary and Quicksand scenes agree on this.
   - **Gridania:** `com0g610`'s local (−130, −1, −320) is the amphitheatre seats at
     (−96.9, 10.6, −1630.8). That is one point, not a checked offset.
3. **Where players stand.** Positions parsed from our own packet logs, and players standing on the
   spot in the test client. A player's y is on the ground by definition, which makes this the best
   source for heights. Camp Black Brush was corrected this way: seed 093 guessed y 201, players
   all over the camp read 200.00, and seed 109 moved the cast down a yalm.
4. **Journal map screenshots.** When a quest has map markers, read them off the journal map.
   - **Central Thanalan:** 100 yalms per grid square, so x = 33 + (gx − 26.7) × 100 and
     z = −482 + (gy − 25.4) × 100.
   - **Ul'dah town map:** 0.5 yalm per pixel at 1280×720. Scale it from two known NPCs and
     line screenshots up on a fixed label.
   - **Grand Company quests:** the `11000000 + index × 100 + n` marker ids don't apply to them.
5. **Probing in the client.** Warp the test character a little above the spot, let it fall and
   read where it lands. The logs record this as `start 250.7 -> y 248.00`. The dungeon monster
   heights were read this way, one probe per cluster of spawns within 4 yalms (see
   [World monsters](world-monsters.md#heights-levels-and-classes)).
6. **Retail video and screenshots.** These are good for arranging a scene, such as who stands where
   around the Stillglade Fane counter, but not for exact coordinates. Treat the result as
   provisional until it has been checked in the client.

## Heights: what goes wrong

- **Floating or sunk NPCs.** The client draws an NPC at the seed's y and does not snap it to the
  ground. An NPC a yalm too high floats, and one too low is waist-deep. Check every new spawn in
  the client.
- **Warp heights.** The y you warp to isn't snapped to the ground either: you land where you fall.
  The y shown on a stand-and-mark is unreliable too. Use the landed y (source 3 or 5).
- **Inside rock.** Spawns can end up inside rock or walls. Spots that turned out unusable:
  - Eastern La Noscea (1045, 46, −943) is inside a rock.
  - Limsa Lominsa (−566, ?, 220) is inside a wall.
  - The first Rootslake spot for Urianger was inside rock. He moved down the gully path to
    (1438.5, −9.5, 1159).
- **Fences and ravines.** A group spread over unknown ground can straddle them. Seed 080 pulled
  the Gridania drill cast into a tight cluster on ground already known to be flat.
- **Pillars and counters.** These hide NPCs and clip the camera. At Ul'dah's airship landing the
  open floor is in front of the counters, not near z 146–151. Thancred moved off a Maelstrom
  Command pillar in seed 128.
- **Origin rows.** A row left at (0, 0, 0) in a field zone is a bug: it needs a real position
  (seed 099's Assessor was one). In a private-area room (0, 0, 0) can be legitimate: the
  Ashcrown Consortium's floor is there.

## Event triggers

- **Push triggers.** These are the invisible circles that start a scene or duty. They fire only
  when the player walks across the circle's edge. Warping inside one does nothing, so place the
  duty's warp-in point outside it, or have the director start the scene itself.
- **In-place duties.** The fight starts where the player stands. The director needs the
  `questBaseRewardSeting` call before its entry EndEvent (see
  [Events and quests](events-and-quests.md)).
- **Spawn ids and actor ids.**
  - **Allocation:** new triggers use fresh `actorClassId`s in the 1090xxx range. Spawn row ids are
    allocated upward and never reused.
  - **Actor numbers:** a spawn's actor number comes from its rank among the zone's root spawns
    (no private area) that have a class path, ordered by id. A new seed's rows therefore land at
    the end of the zone's list and don't renumber anything already placed.

## Shared layouts

- **Grand Company HQs.** Maelstrom Command (232), the Adders' Nest (234) and the Hall of Flames
  (233) share one floor plan:

  | Spot | Position |
  | --- | --- |
  | Door | (160, 0, −155) |
  | Hall | x 151–179, z −160 to −192 |
  | Quartermaster | (171, 0, −180.5), rotation −1.57 |
  | Officer | (171, 0, −175.5), rotation −1.57 |
  | Supply | (171, 0, −170.5), rotation −1.57 |
  | Guide | (163, 0, −166), rotation 0 |
  | Sanction private | (157, 0, −167), rotation 1.57 |

  The Hall of Flames' counter sits further west, so its staff stand at x 169. Talk range is about
  5 yalms.
- **The Bridge.** The Bridge of the Maelstrom (private area `prv_s0_hal01`) reuses Maelstrom
  Command's room, so its scenes run in zone 232.
- **Stillglade Fane.** The conjurers' hall in Gridania (206) has its floor at y 6.82 around
  (−345, −1700).

## Stand-in placements

Some quest locations aren't reachable on our server yet. These quests use a nearby spot instead,
and the seed comments say so:
- **Millers' Glade:** Camp Glory, Coerthas Eastern Lowlands (145, about 1500, 206, 778).
- **Little Ala Mhigo:** Camp Drybone, Eastern Thanalan (171, 1255, 264, −528).
- **Arms Race dealers:** stand-in dealers in Limsa Lominsa (230) near (−570, 18, 206).

## Checking a placement

1. Seed the row, restart the map server (scripts and spawns are loaded once per run) and log in
   nearby.
2. Look at it from a few angles. Is it floating, sunk, inside a wall, facing the wrong way?
3. Tab to it and talk. If you get "You are too far away", you're simply out of talk range.
4. Fix the row with a new seed, not an edit to an old one: seeds are applied in order on existing
   databases. Guard the UPDATE on the old value so it is idempotent, as seed 109 does with
   `AND positionY = 201.0`.

## Regenerating the data page

```bash
python3 tools/npc_placements.py <xivlegacy-server checkout> <npc_names.json> > docs/npc-placements-data.md
```

- **What it reads:** the checkout's `common/sql/schema.sql` and every seed, applied in order to an
  in-memory database.
- **What counts as ours:** seeds 001–051 are the upstream data dump, and everything from 052 on
  is ours.
- **What it records:** each spawn a seed adds, moves or removes, with the comment the seed gives
  for that row.
- **NPC names:** these come from the XIVLegacy Reference build's `npc_names.json`
  (displayNameId → English name).
