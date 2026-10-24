# Test results

Results from driving the real 1.23b client (our native build) against this server, unattended.
The method is described in the client docs:
[Testing](https://github.com/tagban/xivlegacy-client-docs/blob/main/docs/testing.md).

## October 24, 2026: every class, Gridania start

| Class | Opening + combat tutorial | Open-world fight (Central Shroud) |
| --- | --- | --- |
| Gladiator | Pass | Pass (1 kill) |
| Pugilist | Pass | Pass (1 kill) |
| Marauder | Pass | Pass (1 kill) |
| Archer | Pass | Pass (2 kills) |
| Lancer | Pass | Pass (2 kills) |
| Thaumaturge | Server flow verified from logs; automated run pending | Pass (2 kills) |
| Conjurer | Server flow verified from logs; automated run pending | Pass (2 kills) |
| Crafters and gatherers | No combat tutorial for these classes | Not tested; no starter gear |

**Opening + combat tutorial** means a brand-new character goes through:
- the intro and the camera and journal tutorials;
- Yda's walk-up trigger, then talks with Yda and Papalymo;
- the warp into the combat area, the intro, F, the targeting lesson;
- damage and battle complete;
- the closing cutscene and hand-off to Gridania.

**Open-world fight** means a new character of that class starts at a Star Marmot camp, has its
class weapon equipped, draws it, engages a monster and kills it.

## Problems found by these runs

- **The war-class tutorial softlock** (allies finishing the wolves first). Fixed; see
  [Fixes](fixes.md).
- **Crafters and gatherers:** no starter items, and no combat tutorial branch. See
  [Known gaps](known-gaps.md).

## Not yet covered

- The Limsa Lominsa and Ul'dah openings.
- Classes past level 1. Leves and dungeons.
