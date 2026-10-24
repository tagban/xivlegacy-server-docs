# Known gaps

## Gameplay

- **Crafters and gatherers start empty.** `player.lua`'s `initClassItems` has empty branches for
  classes 29–41, so they get no tools or gear at first login. The combat tutorial director has no
  branch for them either, so they skip the fight.
- **Monster stats are placeholders.** HP follows the retail curve; attack, defense and the rest
  use level-scaled fallbacks. See [World monsters](world-monsters.md).
- **About 380 monster entries are skipped** for lack of a client actor class with an appearance.
- **No terrain heights.** Monsters away from known positions can float or sink.

## Streaming

- **50-yalm radius, add-only.**
  - `send_instance_update` only sends actors within 50 yalms, and never removes ones the player
    walks away from.
  - NPCs and monsters pop in late (the Gridania chocobo lender appears only up close), and fields
    look sparse at a distance.
  - A larger radius needs despawn-on-distance first, or the client's actor table fills up.

## Tutorials

- **A double click during a tutorial box** (a type-51 talk) can leave the client waiting; only a
  relog fixes it.
- **Relogging mid-combat-tutorial** at sequence 5 leaves nothing to restart the fight. Logging in
  in the opening zone restarts the whole opening.

## Operations

- **Restarts clear the map server log.** Copy `logs/map-server.log` first if you need it.
- **Applied seeds don't re-apply.** A changed seed has to be applied by hand or added as a new
  file.
