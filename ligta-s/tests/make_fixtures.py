"""Random synthetic instances solved by the paper's Python model, for tests/verify.mjs.

Run:  python3 ligta-s/tests/make_fixtures.py      (writes tests/fixtures/random.json)

Each instance comes from verify_evacuation.random_instance (the generator used in the
paper's verification suite), with a fixed seed. For each one the file stores the instance
in the app's data format and what evacmodel.py computes for it:
  - the lexicographic plan (its unique optimal values: vulnerable placed, placed,
    persons in non-school space / school open space / classrooms, person-minutes),
  - the time-only plan's person-minutes,
  - the nearest-site overflow and person-minutes,
  - the clearance time and the lower bound for the Python plan's supplies,
  - for coverage instances, the greedy and exhaustive siting gains.
Everything is synthetic. No real place, road or shelter is involved.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.normpath(os.path.join(HERE, "..", "..", "research", "safe-shelter-open-schools", "code"))
sys.path.insert(0, CODE)

import evacmodel as em            # noqa: E402
import verify_evacuation as ve    # noqa: E402

SEED = 7202610
N_PLAN = 120
N_SITE = 40


def to_data(inst):
    nodes = [{"id": str(v), "x": 0, "y": 0} for v in inst.nodes]
    roads, seen = [], set()
    for (u, v, tau, cap, tag) in inst.arcs:
        key = (tag, tuple(sorted((u, v))))
        if key in seen:
            continue
        seen.add(key)
        roads.append({"u": str(u), "v": str(v), "tau": int(tau), "cap": int(cap), "tag": tag})
    origins = [{"id": o["id"], "node": str(o["node"]), "pop": o["pop"], "vul": o["vul"],
                "zones": sorted(o["zones"])} for o in inst.origins]
    shelters = []
    for s in inst.shelters:
        # areas that give back the same capacities: C(3.5 c) = c
        shelters.append({"id": s["id"], "node": str(s["node"]), "kind": s["kind"],
                         "areaNonSchool": s["cap_ec"] * 3.5, "areaOpen": s["cap_open"] * 3.5,
                         "rooms": s["rooms"], "learnersPerRoom": s["learners_per_room"],
                         "accessible": bool(s["accessible"]), "zones": sorted(s["zones"])})
    return {"nodes": nodes, "roads": roads, "origins": origins, "shelters": shelters,
            "thetaMax": inst.theta_max}


def num(x):
    return None if x == math.inf else x


def main():
    rng = np.random.default_rng(SEED)
    plans = []
    for i in range(N_PLAN):
        n_nodes = int(rng.integers(12, 26))
        inst = ve.random_instance(rng, n_nodes=n_nodes, n_orig=int(rng.integers(3, 7)),
                                  n_shel=int(rng.integers(3, 8)))
        zones = ["Z"] if i % 3 == 0 else ["Z", "Z2"]
        tags = sorted({a[4] for a in inst.arcs})
        closed = []
        if i % 4 == 1:
            closed = [tags[j] for j in rng.choice(len(tags), size=min(3, len(tags)), replace=False)]
        scen = em.Scenario("S", set(zones), closed_tags=tuple(closed))
        lex = em.lex_plan(inst, scen, "lex")
        blind = em.lex_plan(inst, scen, "blind")
        near = em.nearest_plan(inst, scen)
        sup, caps = em.plan_supplies(inst, lex)
        tclear, _ = em.clearance_time(inst, scen, sup, caps)
        lb = em.clearance_lower_bound(inst, scen, sup, caps)
        plans.append({
            "data": to_data(inst), "scenario": {"zones": zones, "closed": closed},
            "lex": {k: lex[k] for k in ("vul_placed", "placed", "unplaced", "persons_ec",
                                         "persons_open", "persons_room", "person_minutes")},
            "lex_rooms": lex["rooms_closed_total"],
            "lex_schools_used": len(lex["rooms_closed"]),
            "blind": {k: blind[k] for k in ("vul_placed", "placed", "person_minutes")},
            "nearest": {"overflow": near["overflow"], "person_minutes": near["person_minutes"]},
            "supplies": {str(k): v for k, v in sup.items()},
            "caps": {str(k): v for k, v in caps.items()},
            "clearance": num(tclear), "lower_bound": num(lb),
        })
    sites = []
    for i in range(N_SITE):
        inst, cands, caps = ve.random_siting_instance(rng, n_orig=int(rng.integers(5, 9)),
                                                      n_cand=int(rng.integers(5, 9)))
        scen = em.Scenario("S", {"Z"})
        theta = 5
        prob = em.SitingProblem(inst, scen, theta, cands, caps)
        k = int(rng.integers(1, 5))
        g_sites, g_gain = em.greedy_sites(prob, k)
        b_sites, b_gain = em.best_sites(prob, k)
        sites.append({"data": to_data(inst), "scenario": {"zones": ["Z"], "closed": []},
                      "theta": theta, "k": k,
                      "candidates": [{"node": str(c), "area": cap * 3.5} for c, cap in zip(cands, caps)],
                      "phi0": prob.phi0, "greedy_sites": [str(cands[j]) for j in g_sites],
                      "greedy_gain": g_gain, "best_gain": b_gain})
    out = os.path.join(HERE, "fixtures", "random.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump({"seed": SEED, "note": "Synthetic random instances solved by evacmodel.py",
                   "plans": plans, "siting": sites}, f, separators=(",", ":"))
    print("wrote", out, len(plans), "plan instances,", len(sites), "siting instances")


if __name__ == "__main__":
    main()
