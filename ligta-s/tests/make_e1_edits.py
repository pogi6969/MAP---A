"""Random edits of test network E1, solved by the paper's Python model, for tests/verify.mjs.

Run:  python3 ligta-s/tests/make_e1_edits.py      (writes tests/fixtures/e1-edits.json)

Users of the app start from test network E1 and edit it: populations, vulnerable counts,
floor areas, classrooms, accessibility, the trip limit, the active zones and closed bridges.
Each case below is such an edit, chosen at random with a fixed seed, together with what
evacmodel.py computes for it:
  - the lexicographic plan's unique optimal values (vulnerable placed, placed, unplaced,
    persons in non-school space / school open space / classrooms, person-minutes),
  - the time-only plan's vulnerable placed, placed and person-minutes,
  - the nearest-site overflow and person-minutes,
  - the clearance time and the lower bound for the Python plan's supplies.
Only the edited fields are stored; tests/verify.mjs applies them to the E1 data in the app.
Everything is synthetic. No real place, road or shelter is involved.
"""
import copy
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.normpath(os.path.join(HERE, "..", "..", "research", "safe-shelter-open-schools", "code"))
sys.path.insert(0, CODE)

import evacmodel as em            # noqa: E402
import verify_evacuation as ve    # noqa: E402

SEED = 20261017
N_CASES = 100


def main():
    base, _ = ve.build_e1()
    bridges = sorted(base.bridges)
    rng = random.Random(SEED)
    cases = []
    for _ in range(N_CASES):
        inst = copy.deepcopy(base)
        for o in inst.origins:
            if rng.random() < 0.7:
                o["pop"] = rng.randint(0, 900)
                o["vul"] = rng.randint(0, o["pop"])
        shel = []
        for s in inst.shelters:
            area = None
            if rng.random() < 0.5:
                area = rng.choice([0, 350, 700, 1050, 1400, 2100]) + rng.randint(0, 6)
                if s["kind"] == "ec":
                    s["cap_ec"] = em.capacity_from_area(area)
                else:
                    s["cap_open"] = em.capacity_from_area(area)
            if s["kind"] == "school" and rng.random() < 0.5:
                s["rooms"] = rng.randint(0, 30)
                s["learners_per_room"] = rng.randint(20, 45)
            if rng.random() < 0.3:
                s["accessible"] = not s["accessible"]
            shel.append({"id": s["id"], "area": area, "rooms": s["rooms"],
                         "learnersPerRoom": s["learners_per_room"], "accessible": bool(s["accessible"])})
        theta = rng.choice([25, 30, 45, 60, 90, 120])
        inst.theta_max = theta
        zones = sorted(rng.sample(["PDZ", "EDZ", "LAHAR"], rng.randint(1, 3)))
        closed = sorted(rng.sample(bridges, rng.randint(0, 4))) if rng.random() < 0.6 else []
        scen = em.Scenario("S", set(zones), closed_tags=tuple(closed))
        lex = em.lex_plan(inst, scen, "lex")
        blind = em.lex_plan(inst, scen, "blind")
        near = em.nearest_plan(inst, scen)
        sup, caps = em.plan_supplies(inst, lex)
        tclear, _ = em.clearance_time(inst, scen, sup, caps)
        lb = em.clearance_lower_bound(inst, scen, sup, caps)
        cases.append({
            "origins": [[o["id"], o["pop"], o["vul"]] for o in inst.origins],
            "shelters": shel, "thetaMax": theta,
            "scenario": {"zones": zones, "closed": closed},
            "lex": {k: lex[k] for k in ("vul_placed", "placed", "unplaced", "persons_ec",
                                         "persons_open", "persons_room", "person_minutes")},
            "blind": {k: blind[k] for k in ("vul_placed", "placed", "person_minutes")},
            "nearest": {"overflow": near["overflow"], "person_minutes": near["person_minutes"]},
            "supplies": {str(k): v for k, v in sup.items()},
            "caps": {str(k): v for k, v in caps.items()},
            "clearance": None if tclear == math.inf else tclear,
            "lower_bound": None if lb == math.inf else lb,
        })
    out = os.path.join(HERE, "fixtures", "e1-edits.json")
    with open(out, "w") as f:
        json.dump({"seed": SEED, "note": "Random edits of synthetic test network E1 solved by evacmodel.py",
                   "cases": cases}, f, separators=(",", ":"))
    print("wrote", out, len(cases), "edited copies of E1")


if __name__ == "__main__":
    main()
