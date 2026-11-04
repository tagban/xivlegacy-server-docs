# Known gaps

## Gameplay

- **Crafters and gatherers start empty.** `player.lua`'s `initClassItems` has empty branches for
  classes 29–41, so they get no tools or gear at first login. The combat tutorial director has no
  branch for them either, so they skip the fight.
- **Monster stats are placeholders.** HP follows the retail curve; attack, defense and the rest
  use level-scaled fallbacks. See [World monsters](world-monsters.md).
- **About 380 monster entries are skipped** for lack of a client actor class with an appearance.

## Combat

How each combat formula works, and where its numbers came from, is in
[Combat formulas](https://github.com/tagban/xivlegacy-server/blob/develop/docs/combat.md)
in the server repository. What isn't modeled yet:

- **Accuracy, evasion and potency count only what status effects add.** DEX, MND, PIE and gear
  don't change hit, resist or spell size yet, and monsters have none of their own.
- **Player stats are placeholders** (`8 + 2 × level`), since the real 1.x growth curves were never
  reversed.
- **No knockback, no ammo use.** Tempered Will does nothing, and Refill has nothing to refill.
- **Cover, Collusion and Divine Veil's party Regen are partial.** Effect scripts can't reach the
  party or enmity lists yet.
- **Effects kept across a relog restart their full duration.**

## Tutorials

- **A double click during a tutorial box** (a type-51 talk) can leave the client waiting; only a
  relog fixes it.
- **Relogging mid-combat-tutorial** at sequence 5 leaves nothing to restart the fight. Logging in
  in the opening zone restarts the whole opening.

## Operations

- **Restarts clear the map server log.** Copy `logs/map-server.log` first if you need it.
- **Applied seeds don't re-apply.** A changed seed has to be applied by hand or added as a new
  file.
