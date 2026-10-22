# Headroom audit — 2026-10-22

Agent-assisted research session; base `37823dca1bea271510e3ed62205620466ec6f0f9`. The drawn task was `headroom` at priority revision 3. No solver run or frontier change is claimed.

`headroom.json` is the unmodified output of the maintained `tools/headroom.py` on all 20 current archive cases. It improved the plain distance lower bound on all 20. The ranking is by SOL gap to the first archive candidate, which is the minimum-SOL candidate in every current multi-candidate row. It is a ranking of *bound headroom*, not achievable improvement.

The largest gap is `maze-32-32-4-n128`: independent distances total 5926; 43 disjoint forced shortest-path pair conflicts raise the valid SOL/SOC lower bound to 5969. The verified incumbent has SOL 7815, SOC 8225, makespan 125, leaving SOL bound gap 1846. This is a concrete repair target for a next bounded trial; the large gap alone does not predict a better route.

`audit_headroom.py` independently reads the instance/map, checks their hashes, runs grid BFS from every start and goal, rederives each of the 43 forced collisions and their disjointness, and checks the arithmetic against the current archive. `audit-result.json` is its output. The project standalone route checker independently verified the incumbent. Both checks are author-run; they do not constitute independent human review or a tight lower-bound proof.

Reproduce from repository root:

```sh
python tools/headroom.py --out research/<new-session>/headroom.json
python research/c6f353bb2430abaef595df53cb6bad39/audit_headroom.py
python src/verify.py data/instances/maze-32-32-4-n128.json results/repair/maze-32-32-4-n128-random4-s29.json
python tools/check.py --quick
```

The first command requires a fresh output path by design. The audit script reads this package's saved `headroom.json` and writes `audit-result.json` on replay. Resource use: Python 3.14, local macOS, no native solver build; headroom generation took about 2.8 seconds and the independent audit under a second.
