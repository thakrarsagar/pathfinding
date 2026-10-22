"""Independent grid wavefront check of the largest-gap headroom row."""
from collections import deque
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
row = json.loads((HERE / "headroom.json").read_text())[0]
assert row["case"] == "maze-32-32-4-n128"
archive = json.loads((ROOT / "discover/incumbents.json").read_text())
case = next(c for c in archive if c["case"] == row["case"])
raw = (ROOT / case["instance"]).read_bytes()
assert hashlib.sha256(raw).hexdigest() == row["instance_sha256"]
instance = json.loads(raw)
map_raw = (ROOT / instance["map"]).read_bytes()
assert hashlib.sha256(map_raw).hexdigest() == instance["map_sha256"]
lines = map_raw.decode().splitlines()
height, width = int(lines[1].split()[1]), int(lines[2].split()[1])
grid = lines[4:]
assert len(grid) == height and all(len(s) == width for s in grid)
open_cells = {y * width + x for y, s in enumerate(grid) for x, ch in enumerate(s) if ch in ".GS"}


def wavefront(start):
    distances = {start: 0}
    queue = deque([start])
    while queue:
        v = queue.popleft()
        x, y = v % width, v // width
        for xx, yy in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            u = yy * width + xx
            if 0 <= xx < width and 0 <= yy < height and u in open_cells and u not in distances:
                distances[u] = distances[v] + 1
                queue.append(u)
    return distances


starts = [wavefront(s) for s in instance["starts"]]
goals = [wavefront(g) for g in instance["goals"]]
distance = [starts[i][g] for i, g in enumerate(instance["goals"])]
assert sum(distance) == row["individual_distance_bound"]


def forced(i, t):
    if t >= distance[i]:
        return instance["goals"][i]
    positions = [v for v, d in starts[i].items() if d == t and goals[i].get(v) == distance[i] - t]
    return positions[0] if len(positions) == 1 else None


used = set()
for witness in row["disjoint_pair_witnesses"]:
    i, j = witness["agents"]
    t = witness["time"]
    assert i != j and i not in used and j not in used and 1 <= t <= row["horizon"]
    used.update((i, j))
    a, b = forced(i, t), forced(j, t)
    vertex = a is not None and a == b
    swap = a is not None and b is not None and forced(i, t - 1) == b and forced(j, t - 1) == a
    assert vertex if witness["kind"] == "vertex" else swap and witness["kind"] == "edge-swap"

assert row["pair_conflict_bound"] == sum(distance) + len(row["disjoint_pair_witnesses"])
incumbent = json.loads((ROOT / row["incumbent"]["path"]).read_text())
assert incumbent["metrics"] == row["metrics"]
assert row["pair_conflict_bound"] <= min(row["metrics"]["sol"], row["metrics"]["soc"])
result = {
    "case": row["case"],
    "agents": len(distance),
    "individual_distance_bound": sum(distance),
    "verified_disjoint_pair_witnesses": len(row["disjoint_pair_witnesses"]),
    "pair_conflict_bound": row["pair_conflict_bound"],
    "incumbent_sol": row["metrics"]["sol"],
    "remaining_sol_gap": row["sol_gap"],
}
(HERE / "audit-result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
