"""Export the synthetic test network E1 from the research code to src/e1-data.json.

Run from anywhere:  python3 ligta-s/src/export_e1.py
The app's demo dataset is built from the same function (verify_evacuation.build_e1)
that produced the numbers in the paper, so the app and the paper use one network.
Everything in it is synthetic: no real barangay, road, school or shelter.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.normpath(os.path.join(HERE, "..", "..", "research", "safe-shelter-open-schools", "code"))
sys.path.insert(0, CODE)

import evacmodel as em            # noqa: E402
import verify_evacuation as ve    # noqa: E402

inst, pos = ve.build_e1()

TOWN = {"TE": "East town", "TNE": "North-east town", "TSE": "South-east town",
        "TS": "South town", "TSW": "South-west town"}


def compass(x, y):
    b = (90 - math.degrees(math.atan2(y, x))) % 360
    names = ["north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west"]
    return names[int(((b + 22.5) % 360) // 45)]


nodes = []
for k, (x, y) in pos.items():
    kind = "ring" if k.startswith("R") else ("town" if k.startswith("T") else "origin")
    nodes.append({"id": k, "x": round(x, 3), "y": round(y, 3), "kind": kind,
                  "name": TOWN.get(k, k)})

roads = []
seen = set()
for (u, v, tau, cap, tag) in inst.arcs:
    key = (tag, tuple(sorted((u, v))))
    if key in seen:
        continue
    seen.add(key)
    roads.append({"u": u, "v": v, "tau": tau, "cap": cap, "tag": tag})

ZONE_NAME = {"PDZ": "6-km Permanent Danger Zone", "EDZ": "Extended Danger Zone (7 km, south flank)",
             "LAHAR": "Lahar-prone area"}
origins = []
for o in inst.origins:
    x, y = pos[o["node"]]
    r = math.hypot(x, y)
    origins.append({"id": o["id"],
                    "name": "%s, %s slope (%.1f km)" % (o["id"], compass(x, y), r),
                    "node": o["node"], "zones": sorted(o["zones"]),
                    "pop": o["pop"], "vul": o["vul"]})

shelters = []
for s in inst.shelters:
    shelters.append({"id": s["id"], "name": s["name"], "node": s["node"], "kind": s["kind"],
                     "areaNonSchool": s["area"] if s["kind"] == "ec" else 0,
                     "areaOpen": s["area"] if s["kind"] == "school" else 0,
                     "rooms": s["rooms"], "learnersPerRoom": s["learners_per_room"],
                     "accessible": bool(s["accessible"]), "zones": sorted(s["zones"])})
    # check that the areas reproduce the capacities used by the paper
    sh = shelters[-1]
    assert em.capacity_from_area(sh["areaNonSchool"]) == s["cap_ec"], s["id"]
    assert em.capacity_from_area(sh["areaOpen"]) == s["cap_open"], s["id"]

bridges = sorted(inst.bridges)
scen = ve.e1_scenarios()
scenarios = [{"id": "AL3", "name": "Alert Level 3", "zones": ["PDZ"], "closed": []},
             {"id": "AL4", "name": "Alert Level 4", "zones": ["PDZ", "EDZ"], "closed": []},
             {"id": "AL4+L", "name": "Alert Level 4 + lahar", "zones": ["EDZ", "LAHAR", "PDZ"],
              "closed": list(ve.ALL_BRIDGES)}]
for a, b in zip(scenarios, scen):
    assert set(a["zones"]) == b.zones and tuple(a["closed"]) == tuple(b.closed_tags)

cands = ["TS", "TSW", "TNE", "TE", "TSE"]
area_new = [1400, 1050, 1225, 1050, 875]
candidates = [{"node": n, "name": "Ligtas Pinoy Center, " + TOWN[n], "area": a}
              for n, a in zip(cands, area_new)]

data = {
    "format": "ligta-s/1",
    "name": "Test network E1 (synthetic volcano)",
    "synthetic": True,
    "note": "Synthetic test network from the paper (verify_evacuation.build_e1). Not real Albay data.",
    "units": {"x": "km east of the summit", "y": "km north of the summit", "tau": "minutes",
              "cap": "evacuees per minute"},
    "nodes": nodes, "roads": roads, "origins": origins, "shelters": shelters,
    "zones": [{"id": k, "name": v} for k, v in ZONE_NAME.items()],
    "channels": [{"id": c, "bearing": d, "bridges": [b for b in bridges if inst.bridges[b] == c]}
                 for c, d in ve.CHANNELS.items()],
    "scenarios": scenarios,
    "thetaMax": inst.theta_max, "thetaSite": ve.THETA_SITE, "candidates": candidates,
    # drawing only (the model never reads it): the same shapes as the paper's Figure of E1
    "geo": {"summit": [0, 0], "pdzRadius": 6.0,
            "edz": {"r0": 6.0, "r1": 7.0, "from": 200, "to": 340},
            "channelRange": [1.5, 14.5]},
}
out = os.path.join(HERE, "e1-data.json")
with open(out, "w") as f:
    json.dump(data, f, indent=1)
print("wrote", out, len(nodes), "nodes", len(roads), "roads", "bridges", bridges)
