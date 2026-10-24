# Events and quests

## The event round trip

1. The client sends **Event Start** (`0x012D`) for an actor with an event name: `talkDefault`,
   `pushDefault`, `noticeEvent`, `commandDefault`, `commandForced` or `commandRequest`.
2. The map server routes it, in this order:
   1. Resume a coroutine already parked on this player's event, if its owner matches.
   2. Hotbar commands (`commandDefault` on `0xA0F0xxxx`) go to the battle command handler.
   3. Content directors get `onEventStarted`.
   4. Every active quest gets its hook: `onTalk`, `onPush`, `onEmote` or `onCommand`.
   5. The target actor's own script gets `onEventStarted` (menus such as aetherytes, shops and the
      chocobo lender).
   6. Command scripts (`commands/<Name>.lua`, e.g. `ActivateCommand` for F).
3. Scripts call `callClientFunction(player, fn, …)`. That sends **Run Event Function** (`0x0130`)
   and parks the coroutine until the client's **Event Update** (`0x012E`) carries the result back.
4. `player:EndEvent()` sends **End Event** (`0x0131`), and the client is free again.

The client only allows one event at a time and blocks movement, talking, F and attacks while one is
open. So every path through a script has to end the event exactly once, and nothing else may end it
early. Most of the bugs we fixed broke one of those two rules (see [Fixes](fixes.md)).

## The coroutine scheduler

Scripts run as Lua coroutines and park by yielding one of three things:

| Yield | Helper | Resumes on |
| --- | --- | --- |
| `_WAIT_EVENT` | `callClientFunction`, `kickEventContinue` | The client's Event Update or Event Start for that player |
| `_WAIT_TIME` | `wait(seconds)` | The ticker |
| `_WAIT_SIGNAL` | `waitForSignal(name)` | `sendSignal(name)` or a server-side signal |

- **Signals are global by name:** firing one resumes every coroutine parked on that name, and if
  nothing is waiting, the signal is simply lost.
- **The heartbeat:** the ticker logs how many coroutines wait on each kind every 10 seconds.

### Signals the combat tutorials use

| Signal | Fired by |
| --- | --- |
| `playerActive` | F (ActivateCommand) |
| `playerAttack` | Each player swing in a content fight |
| `tpOver1000` | TP reaching 1,000 |
| `weaponskillUsed` | A player weaponskill |
| `battleComplete` | The last enemy in the content roster dying. Any pending fight milestone is released first (our fix) |

## Quest hooks

Every talk fans out to every active quest's `onTalk`. Quest scripts filter by the NPC's class id
and often end with a generic `player:EndEvent()`.

- **Populace NPCs with their own menu script** (`PopulaceChocoboLender`, shops, leve publishers):
  the fan-out runs only when a quest registered that NPC with `quest:SetENpc`. Otherwise the
  quest's End Event closed the NPC's conversation.
- **`PopulaceStandard` NPCs** keep the every-quest fan-out, because unfinished quests don't
  register their NPCs.

## Directors and the opening tutorials

The opening quests (`man0l0` Limsa, `man0g0` Gridania, `man0u0` Ul'dah) drive the first hour.

- **Login in a city's opening zone** with the opening quest active starts the `OpeningDirector`,
  kicks its notice event and **clears the quest's data and flags**. So relogging there restarts
  the opening.
- **The combat tutorial** is a content area with its own director (`QuestDirectorMan0g001` and its
  Limsa and Ul'dah counterparts). Its branches:
  - **Disciples of War:** `processTtrBtl001` (draw-weapon lesson) → wait `playerActive` → kick →
    `processTtrBtl002` (targeting lesson) → wait `playerAttack`, `tpOver1000`, `weaponskillUsed`
    and `battleComplete`, with a tutorial tip at each.
  - **Disciples of Magic:** `processTtrBtlMagic001` → kick → `processTtrBtl002` → end the event →
    wait `battleComplete`.
  - **Anything else** (crafters, gatherers) skips the fight entirely.
- **The ending:** music, then `processEvent020_1` (closing cutscene and item dialog), the next
  quest sequence, `ContentFinished`, and a warp into the city.

## Player snapshots

Scripts see the player through a snapshot built when the hook runs. Several snapshots were built
by hand and left fields at their defaults; gil was always 0, for example. When adding a field,
check every `PlayerSnapshot { … }` literal, not only the main builder.
