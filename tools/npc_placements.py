#!/usr/bin/env python3
"""Build docs/npc-placements-data.md: every NPC, trigger and quest-fight
spawn our seeds add, move or remove, with the seed and the note beside it.

    python3 tools/npc_placements.py <server checkout> <npc_names.json> > docs/npc-placements-data.md

<server checkout> is a tagban/xivlegacy-server tree (common/sql/schema.sql and
common/sql/seed/). The seeds are applied in order to an in-memory database;
everything from seed 052 on is ours (001-051 are the upstream data dump).
<npc_names.json> maps displayNameId -> English name (the Reference build cache).
"""
import json, os, re, sqlite3, sys
from collections import defaultdict

src, names_path = sys.argv[1], sys.argv[2]
names = json.load(open(names_path))
seed_dir = os.path.join(src, 'common/sql/seed')
db = sqlite3.connect(':memory:')
db.executescript(open(os.path.join(src, 'common/sql/schema.sql')).read())

SC = ('actorClassId,uniqueId,zoneId,privateAreaName,privateAreaLevel,'
      'positionX,positionY,positionZ,rotation')
BC = 'groupId,positionX,positionY,positionZ,rotation'
SKIP_B = {'101_world_monster_spawns.sql', '130_dungeon_monsters.sql'}  # own page


def notes_for(path):
    """id or uniqueId -> the comment nearest above (or beside) the line naming it."""
    out, block = {}, []
    for line in open(path):
        s = line.strip()
        if s.startswith('--'):
            block.append(s[2:].strip())
            continue
        if not s:
            block = []
            continue
        code, _, tail = s.partition('--')
        note = tail.strip() or ' '.join(block)
        keys = []
        m = re.match(r'\((\d+)\s*,\s*(\d+)\s*,\s*\'([^\']*)\'', code)
        if m:
            keys = [int(m.group(1)), m.group(3)]
        elif re.match(r'\((\d+)\s*,', code):
            keys = [int(re.match(r'\((\d+)', code).group(1))]
        else:
            for a, b in re.findall(r'id"?\s+BETWEEN\s+(\d+)\s+AND\s+(\d+)', code):
                keys += range(int(a), int(b) + 1)
            for group in re.findall(r'(?<![A-Za-z])"?id"?\s*(?:=|IN\s*\()\s*([\d,\s]+)', code):
                keys += [int(i) for i in re.findall(r'\d+', group)]
            keys += re.findall(r"'([a-z0-9_]+)'", code) if 'uniqueId' in code else []
        for k in keys:
            out.setdefault(k, note)
    return out


def battle():
    try:
        return {r[0]: r[1:] for r in db.execute(
            f'select bnpcId,{BC} from server_battlenpc_spawn_locations')}
    except sqlite3.OperationalError:  # before seed 021 creates the table
        return {}


def note_of(notes, k, row):
    return notes.get(k) or (row and notes.get(row[1])) or ''


events = []
prev = prevb = None
for seed in sorted(os.listdir(seed_dir)):
    db.executescript(open(os.path.join(seed_dir, seed)).read())
    cur = {r[0]: r[1:] for r in db.execute(f'select id,{SC} from server_spawn_locations')}
    curb = battle()
    if prev is not None and seed >= '052':
        notes = notes_for(os.path.join(seed_dir, seed))
        for k, v in cur.items():
            if k not in prev:
                events.append(('add', seed, k, None, v, note_of(notes, k, cur.get(k) or prev.get(k))))
            elif prev[k][2:] != v[2:]:
                events.append(('move', seed, k, prev[k], v, note_of(notes, k, cur.get(k) or prev.get(k))))
        for k in prev.keys() - cur.keys():
            events.append(('del', seed, k, prev[k], None, note_of(notes, k, cur.get(k) or prev.get(k))))
        if seed not in SKIP_B:
            for k, v in curb.items():
                if k not in prevb:
                    events.append(('badd', seed, k, None, v, notes.get(k, '')))
                elif prevb[k] != v:
                    events.append(('bmove', seed, k, prevb[k], v, notes.get(k, '')))
    prev, prevb = cur, curb

zones = {r[0]: (r[1] or '', r[2] or '') for r in db.execute(
    'select id, zoneName, placeName from server_zones')}
cls = {r[0]: r[1] for r in db.execute('select id, displayNameId from gamedata_actor_class')}
group_class = {r[0]: r[1] for r in db.execute(
    'select g.groupId, p.actorClassId from server_battlenpc_groups g '
    'join server_battlenpc_pools p on p.poolId = g.poolId')}
group_zone = {r[0]: r[1] for r in db.execute('select groupId, zoneId from server_battlenpc_groups')}


def who(class_id):
    n = names.get(str(cls.get(class_id) or '')) or names.get(str(class_id))
    return n or ''


def zone_title(z):
    name, place = zones.get(z, ('', ''))
    return f'{z} {place or name}'.strip() + (f' ({name})' if place and name else '')


def f(v):
    if v is None:
        return ''
    return (f'{v:.2f}'.rstrip('0').rstrip('.') or '0').replace('-0', '0') if abs(v) < 0.005 else f'{v:.2f}'.rstrip('0').rstrip('.')


def seed_link(seed):
    return f'[{seed[:3]}](https://github.com/tagban/xivlegacy-server/blob/develop/common/sql/seed/{seed})'


def clean(note):
    note = note.replace('|', '/').strip()
    return note if len(note) <= 140 else note[:137].rsplit(' ', 1)[0] + '…'


print('# NPC placement data\n')
print('Generated by `tools/npc_placements.py` from the seeds on `develop`; do not edit by hand.')
print('Coordinates are world units (x east, y up, z south); rotation is radians.')
print('See [NPC and quest placement](npc-placements.md) for how these were found.\n')

moves = [e for e in events if e[0] == 'move']
print('## Moved spawns\n')
print('Rows a later seed corrected. **Δy** is the height change.\n')
print('| Seed | Zone | Spawn | NPC | From (x, y, z) | To (x, y, z) | Δy | Note |')
print('| --- | --- | --- | --- | --- | --- | --- | --- |')
for _, seed, k, a, b, note in moves:
    dy = b[6] - a[6]
    if a[2:5] != b[2:5]:
        where = lambda r: f'{r[2]}' + (f' {r[3]}/{r[4]}' if r[3] else '')
        note = f'Zone {where(a)} → {where(b)}. ' + note
    print(f'| {seed_link(seed)} | {b[2]} | {k} `{b[1]}` | {who(b[0])} ({b[0]}) '
          f'| {f(a[5])}, {f(a[6])}, {f(a[7])} | {f(b[5])}, {f(b[6])}, {f(b[7])} '
          f'| {dy:+.1f} | {clean(note)} |')

bm = [e for e in events if e[0] == 'bmove']
if bm:
    print('\n## Moved quest-fight spawns\n')
    print('| Seed | Battle NPC | Group | From (x, y, z) | To (x, y, z) | Δy | Note |')
    print('| --- | --- | --- | --- | --- | --- | --- |')
    for _, seed, k, a, b, note in bm:
        print(f'| {seed_link(seed)} | {k} | {b[0]} | {f(a[1])}, {f(a[2])}, {f(a[3])} '
              f'| {f(b[1])}, {f(b[2])}, {f(b[3])} | {b[2] - a[2]:+.1f} | {clean(note)} |')

dels = [e for e in events if e[0] == 'del']
if dels:
    print('\n## Removed spawns\n')
    print('| Seed | Zone | Spawn | NPC | Was at (x, y, z) | Note |')
    print('| --- | --- | --- | --- | --- | --- |')
    for _, seed, k, a, _, note in dels:
        print(f'| {seed_link(seed)} | {a[2]} | {k} `{a[1]}` | {who(a[0])} ({a[0]}) '
              f'| {f(a[5])}, {f(a[6])}, {f(a[7])} | {clean(note)} |')

# Final position of every spawn we added, by zone.
final = {}
for kind, seed, k, a, b, note in events:
    if kind == 'add':
        final[k] = [seed, b, note]
    elif kind == 'move' and k in final:
        final[k][1] = b
    elif kind == 'del':
        final.pop(k, None)
restored = {k: v for k, v in final.items() if v[0].startswith('059')}
ours = {k: v for k, v in final.items() if k not in restored}

print('\n## Added NPCs and triggers by zone\n')
print('Where each spawn stands now (after every later fix). Private area is '
      '`name/level` when the spawn only exists in that instance.\n')
byzone = defaultdict(list)
for k, (seed, b, note) in ours.items():
    byzone[b[2]].append((k, seed, b, note))
for z in sorted(byzone):
    print(f'### {zone_title(z)}\n')
    print('| Spawn | NPC | x | y | z | Rot | Private area | Seed | Note |')
    print('| --- | --- | --- | --- | --- | --- | --- | --- | --- |')
    for k, seed, b, note in sorted(byzone[z]):
        pa = f'{b[3]}/{b[4]}' if b[3] else ''
        print(f'| {k} `{b[1]}` | {who(b[0])} ({b[0]}) | {f(b[5])} | {f(b[6])} | {f(b[7])} '
              f'| {b[8]:.2f} | {pa} | {seed_link(seed)} | {clean(note)} |')
    print()

badds = [e for e in events if e[0] == 'badd']
if badds:
    print('## Quest-fight spawns\n')
    print('Battle NPCs our quest seeds add (open-world and dungeon monsters are on '
          '[World monsters](world-monsters.md)). Final positions.\n')
    print('| Battle NPC | Group | Zone | Monster | x | y | z | Seed | Note |')
    print('| --- | --- | --- | --- | --- | --- | --- | --- | --- |')
    cur_b = battle()
    for _, seed, k, _, b, note in badds:
        b = cur_b.get(k, b)
        c = group_class.get(b[0])
        mon = f'{who(c)} ({c})' if c else ''
        print(f'| {k} | {b[0]} | {group_zone.get(b[0], "")} | {mon} | {f(b[1])} | {f(b[2])} '
              f'| {f(b[3])} | {seed_link(seed)} | {clean(note)} |')
    print()

print('## Restored private-area spawns\n')
print('Seed 059 put back the private-area NPCs the upstream dump had lost (the '
      'opening tutorials\' instanced casts). Listed for completeness.\n')
print('<details><summary>' + str(len(restored)) + ' spawns</summary>\n')
print('| Spawn | NPC | Zone | x | y | z | Private area |')
print('| --- | --- | --- | --- | --- | --- | --- |')
for k, (seed, b, note) in sorted(restored.items()):
    print(f'| {k} `{b[1]}` | {who(b[0])} ({b[0]}) | {b[2]} | {f(b[5])} | {f(b[6])} | {f(b[7])} '
          f'| {b[3]}/{b[4]} |')
print('\n</details>')
