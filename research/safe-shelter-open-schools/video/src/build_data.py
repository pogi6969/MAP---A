"""Export the synthetic test network E1 and its plans for the LIGTA-S video.

Everything here is computed with the project's own model (code/evacmodel.py)
and the test network E1 (code/verify_evacuation.py, build_e1), then checked
against code/results.json so that the video cannot show a number the paper
does not report. Output: src/data.json (read by render.js).

Run:  python3 build_data.py
"""
import json
import math
import os
import sys

import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.normpath(os.path.join(HERE, "..", "..", "code"))
sys.path.insert(0, CODE)

import evacmodel as em  # noqa: E402
import verify_evacuation as ve  # noqa: E402

RES = json.load(open(os.path.join(CODE, "results.json")))
E1 = RES["e1"]


def path_nodes(inst, scen, src, dst):
    """Fastest road path (list of node ids) from src to dst."""
    G = nx.DiGraph()
    for (u, v, tau, cap, tag) in inst.open_arcs(scen.closed_tags):
        if not G.has_edge(u, v) or G[u][v]["weight"] > tau:
            G.add_edge(u, v, weight=tau)
    return nx.shortest_path(G, src, dst, weight="weight")


def plan_streams(inst, scen, plan):
    """Aggregate a plan into (origin, shelter, tier) streams with paths."""
    agg = {}
    for (a, k, cls), f in plan["x"].items():
        s, tier, cap, acc = plan["slots"][k]
        key = (a, s, tier)
        agg[key] = agg.get(key, 0) + f
    out = []
    for (a, s, tier), f in sorted(agg.items()):
        o, sh = inst.origins[a], inst.shelters[s]
        out.append({"origin": o["id"], "shelter": sh["id"], "tier": tier, "persons": f,
                    "minutes": int(plan["T"][a][s]),
                    "path": path_nodes(inst, scen, o["node"], sh["node"])})
    return out


def crossing_point(p, q, deg, r0=1.0, r1=16.0):
    """Point where segment p-q crosses the channel ray at bearing deg."""
    t = math.radians(deg)
    a = (r0 * math.cos(t), r0 * math.sin(t))
    b = (r1 * math.cos(t), r1 * math.sin(t))
    d1 = (q[0] - p[0], q[1] - p[1])
    d2 = (b[0] - a[0], b[1] - a[1])
    den = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(den) < 1e-12:
        return None
    s = ((a[0] - p[0]) * d2[1] - (a[1] - p[1]) * d2[0]) / den
    return (p[0] + s * d1[0], p[1] + s * d1[1])


def main():
    inst, pos = ve.build_e1()
    al3 = em.Scenario("AL3", {"PDZ"})
    al4 = em.Scenario("AL4", {"PDZ", "EDZ"})
    al4l = em.Scenario("AL4+L", {"PDZ", "EDZ", "LAHAR"}, closed_tags=ve.ALL_BRIDGES)

    # ---- plans at Alert Level 3 -------------------------------------------
    near = em.nearest_plan(inst, al3)
    blind = em.lex_plan(inst, al3, "blind")
    lex = em.lex_plan(inst, al3, "lex")
    r3 = E1["scenarios"]["AL3"]
    assert near["overflow"] == r3["nearest_overflow"] == 298
    assert blind["rooms_closed_total"] == r3["blind"]["rooms_closed_total"] == 40
    assert blind["learners_displaced"] == r3["blind"]["learners_displaced"] == 1702
    assert lex["rooms_closed_total"] == r3["lex"]["rooms_closed_total"] == 14
    assert lex["learners_displaced"] == r3["lex"]["learners_displaced"] == 532
    assert round(blind["mean_time"], 2) == 29.48 and round(lex["mean_time"], 2) == 31.18

    T = em.travel_times(inst, em.Scenario("open", set()))
    nearest = []
    site_cap = {}
    for sh in inst.shelters:
        site_cap[sh["node"]] = site_cap.get(sh["node"], 0) + sh["cap_ec"] + sh["cap_open"] + sh["rooms"] * sh["q"]
    for a, o in enumerate(inst.origins):
        if al3.demand(o) == 0:
            continue
        t, s = min((T[a][s], s) for s in range(len(inst.shelters)))
        node = inst.shelters[s]["node"]
        nearest.append({"origin": o["id"], "node": node, "minutes": int(t), "persons": o["pop"],
                        "path": path_nodes(inst, al3, o["node"], node)})
    near_sites = [{"node": n, "load": l, "cap": site_cap[n], "over": max(0, l - site_cap[n])}
                  for n, l in near["load"].items()]

    # ---- per-minute arrival curve and bisection at AL3 --------------------
    sup, caps = em.plan_supplies(inst, lex)
    total = sum(sup.values())
    curve = [em.arrivals_by(inst, al3, t, sup, caps) for t in range(0, 61)]
    tstar, _ = em.clearance_time(inst, al3, sup, caps)
    lb = em.clearance_lower_bound(inst, al3, sup, caps)
    assert tstar == r3["clearance_lex"] == 53 and lb == r3["clearance_lb"] == 34
    assert curve[53] == total == 1560 and curve[52] < total
    steps = []
    hi = 8
    while em.arrivals_by(inst, al3, hi, sup, caps) < total:
        steps.append({"kind": "double", "T": hi, "F": em.arrivals_by(inst, al3, hi, sup, caps)})
        hi *= 2
    steps.append({"kind": "double", "T": hi, "F": total})
    lo = -1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        F = em.arrivals_by(inst, al3, mid, sup, caps)
        steps.append({"kind": "bisect", "T": mid, "F": F, "ok": F >= total})
        if F >= total:
            hi = mid
        else:
            lo = mid
    assert hi == 53

    # ---- compound scenario: lahar pocket ----------------------------------
    lexL = em.lex_plan(inst, al4l, "lex")
    assert lexL["unplaced"] == E1["channel_closures"]["A+B"]["unplaced"] == 450

    # ---- geometry ----------------------------------------------------------
    roads = {}
    for (u, v, tau, cap, tag) in inst.arcs:
        key = tuple(sorted((u, v)))
        if key in roads:
            continue
        if tag.startswith("ring") or (u.startswith("R") and v.startswith("R")):
            kind = "ring"
        elif u.startswith("O") or v.startswith("O"):
            kind = "local"
        elif u.startswith("R") or v.startswith("R"):
            kind = "highway"
        else:
            kind = "outer"
        roads[key] = {"u": key[0], "v": key[1], "tau": tau, "cap": cap, "tag": tag, "kind": kind}
    bridges = []
    for r in roads.values():
        if r["tag"] in ve.ALL_BRIDGES:
            deg = ve.CHANNELS[r["tag"][0]]
            p = crossing_point(pos[r["u"]], pos[r["v"]], deg)
            bridges.append({"tag": r["tag"], "u": r["u"], "v": r["v"], "x": p[0], "y": p[1]})

    data = {
        "note": "Synthetic test network E1 from code/verify_evacuation.py; not Albay data.",
        "pos": {k: [round(v[0], 4), round(v[1], 4)] for k, v in pos.items()},
        "roads": list(roads.values()),
        "bridges": sorted(bridges, key=lambda b: b["tag"]),
        "channels": ve.CHANNELS,
        "origins": [{"id": o["id"], "node": o["node"], "pop": o["pop"], "vul": o["vul"],
                     "zone": sorted(o["zones"])[0]} for o in inst.origins],
        "shelters": [{"id": s["id"], "name": s["name"], "node": s["node"], "kind": s["kind"],
                      "cap_ec": s["cap_ec"], "cap_open": s["cap_open"], "rooms": s["rooms"],
                      "room_cap": s["rooms"] * s["q"], "accessible": s["accessible"],
                      "learners_per_room": s["learners_per_room"]} for s in inst.shelters],
        "towns": {"TE": "east town", "TNE": "northeast town", "TSE": "southeast city",
                  "TS": "south town", "TSW": "southwest town"},
        "al3": {
            "demand": lex["demand"], "vulnerable": lex["vulnerable"],
            "nearest": nearest, "nearest_sites": near_sites, "nearest_overflow": near["overflow"],
            "blind": {"streams": plan_streams(inst, al3, blind),
                      "rooms": {inst.shelters[s]["id"]: k for s, k in blind["rooms_closed"].items()},
                      "rooms_total": blind["rooms_closed_total"],
                      "learners": blind["learners_displaced"],
                      "mean": round(blind["mean_time"], 2),
                      "persons_ec": blind["persons_ec"], "persons_open": blind["persons_open"],
                      "persons_room": blind["persons_room"]},
            "lex": {"streams": plan_streams(inst, al3, lex),
                    "rooms": {inst.shelters[s]["id"]: k for s, k in lex["rooms_closed"].items()},
                    "rooms_total": lex["rooms_closed_total"],
                    "learners": lex["learners_displaced"],
                    "mean": round(lex["mean_time"], 2),
                    "persons_ec": lex["persons_ec"], "persons_open": lex["persons_open"],
                    "persons_room": lex["persons_room"]},
            "curve": curve, "tstar": tstar, "lb": lb, "steps": steps,
        },
        "al4": E1["scenarios"]["AL4"]["lex"] | {"demand": E1["scenarios"]["AL4"]["demand"]},
        "closures": E1["channel_closures"],
        "pocket": {"unplaced": lexL["unplaced"], "origins": ["O3", "O4"], "school": "SCH1"},
        "siting": E1["siting"],
        "verification": RES["verification"],
    }
    with open(os.path.join(HERE, "data.json"), "w") as f:
        json.dump(data, f, indent=1, default=lambda x: None if x == math.inf else x)
    print("wrote data.json; AL3 bisection:", [(s["kind"], s["T"]) for s in steps])
    print("blind streams:", [(s["origin"], s["shelter"], s["tier"], s["persons"]) for s in data["al3"]["blind"]["streams"]])
    print("nearest:", [(n["origin"], n["node"], n["minutes"]) for n in nearest], near_sites)


if __name__ == "__main__":
    main()
