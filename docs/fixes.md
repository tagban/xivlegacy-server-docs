# Fixes and contributions

Every change we made to Garlemald, why, and where it lives. Upstream pull requests target
`swstegall/Garlemald-Server` `develop`. Local commits are on our fork's `fix/end-event-current-name`
branch.

| Fix | Symptom | Cause | Where |
| --- | --- | --- | --- |
| Magic-class combat tutorial ends its event | THM/CNJ starters couldn't draw a weapon or attack in the opening fight | The magic branch kicked a second notice event and never ended it, so the client stayed in event mode | [#212](https://github.com/swstegall/Garlemald-Server/pull/212) (open) |
| Standard init for script-less monster classes | The client crashed when the first open-world monster streamed in | Monster classes without a base script got the townsperson init values, and the client raised an exception | [#213](https://github.com/swstegall/Garlemald-Server/pull/213) (open) |
| Real gil in NPC scripts | The chocobo lender never offered a rental | The player snapshot hard-coded `current_gil: 0`; hand-built snapshots in the talk dispatch, kill hook and quest hooks did too | [#214](https://github.com/swstegall/Garlemald-Server/pull/214) (open) |
| Quest talk hooks skip menu NPCs they didn't register | The rental menu never answered | Man0g1's `onTalk` ran for the lender too, and its generic `EndEvent` closed the lender's conversation after the welcome line | [#215](https://github.com/swstegall/Garlemald-Server/pull/215) (open) |
| Open-world monsters | Empty fields | No spawn data; boot never spawned battle NPCs | [#216](https://github.com/swstegall/Garlemald-Server/pull/216) (open) — see [World monsters](world-monsters.md) |
| Combat tutorial releases pending milestones | War-class tutorial hung after the wolves died | Allies could finish the fight before the player's weaponskill; `battleComplete` then found nothing waiting | [#224](https://github.com/swstegall/Garlemald-Server/pull/224) (open) |
| Limsa (Rostnsthal) tutorial: end the current event, queue a talk made mid-push | Clicking an NPC during the targeting tutorial broke the flow | `EndEvent` used a stale event name; a talk during a push event resumed the wrong coroutine | [#223](https://github.com/swstegall/Garlemald-Server/pull/223) (open) |
| Login snapshot carries the quest journal ([issue #197](https://github.com/swstegall/Garlemald-Server/issues/197)) | A relog mid-opening stranded the player | `HasQuest()` was always false at login, so the reconnect branches never ran; a SEQ_005 relog now restarts SEQ_000 | [#217](https://github.com/swstegall/Garlemald-Server/pull/217) (open) |
| `player:SetEventStatus` works ([#187](https://github.com/swstegall/Garlemald-Server/issues/187)) | Tutorial push-trigger toggles never reached the client | The binding discarded its arguments | [#218](https://github.com/swstegall/Garlemald-Server/pull/218) (open) |
| `run-all` checks ports and reports dead services ([#211](https://github.com/swstegall/Garlemald-Server/issues/211)) | A half-dead stack behind an "all running" banner | No pre-flight check or supervision | [#219](https://github.com/swstegall/Garlemald-Server/pull/219) (open) |
| Session-end confirm reports success ([#196](https://github.com/swstegall/Garlemald-Server/issues/196)) | World logged "error ending session" on every disconnect and skipped its cleanup | Error code 1 was hard-coded | [#220](https://github.com/swstegall/Garlemald-Server/pull/220) (open) |
| Game-message actor params ([#202](https://github.com/swstegall/Garlemald-Server/issues/202)) | "Ankle Biter:  is engaged." and blank "Protect  from harm." | `<displayName>` comes from a type-6 actor param; integers render blank (probed live) | [#221](https://github.com/swstegall/Garlemald-Server/pull/221) (open) |
| Session end despawns the player and its content run ([#195](https://github.com/swstegall/Garlemald-Server/issues/195), [#194](https://github.com/swstegall/Garlemald-Server/issues/194)) | Ghost players; content monsters leaking into the base zone | Session end never removed the actor or tore down content | [#222](https://github.com/swstegall/Garlemald-Server/pull/222) (open) |

## Investigations

- **[#203](https://github.com/swstegall/Garlemald-Server/issues/203), linkpearl freeze:** not reproducible on current code. The full Baderon → linkpearl → NPC Linkpearls → free movement flow works. [Comment with the trace](https://github.com/swstegall/Garlemald-Server/issues/203#issuecomment-6391337565).

## How each was verified

- **Upstream PRs:**
  - Garlemald's CI gates: `cargo fmt --check`, `clippy -D warnings`, workspace build and tests
    (892), and the Lua walkthroughs in `content-test` (23/23).
  - A live check on our server with the native client: the THM opening fight, the first funguar
    spawn, the chocobo rental end to end, and kill speed at retail HP.
- **The milestone fix:** an automated Gladiator run through the opening tutorial (see
  [Test results](test-results.md)).

## Conventions we follow for upstream

- One fix per pull request, branched from the latest `develop`.
- The pull request description states the symptom, the cause as seen in the logs, the fix and the
  verification.
