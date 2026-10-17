"""Verification suite, computational cost, and worked instance E1.

Run:  python3 verify_evacuation.py            (writes results.json and figures/)

Every check compares the model code in evacmodel.py with an independently
written reference (linear programs, a mixed-integer program, a linear scan,
or exhaustive search) on random synthetic instances. No real shelter, school,
or road is used; all inputs are synthetic.
"""

import itertools
import json
import math
import os
import sys
import time

import numpy as np
from scipy.optimize import LinearConstraint, linprog, milp, Bounds

import evacmodel as em

SEED = 20261017
THETA_SITE = 30
HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")
os.makedirs(FIG, exist_ok=True)


# ---------------------------------------------------------------------------
# Random synthetic instances
# ---------------------------------------------------------------------------

def random_instance(rng, n_nodes=22, n_orig=5, n_shel=6, theta=None, two_zones=True):
    pts = rng.uniform(0.0, 10.0, size=(n_nodes, 2))
    d = np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=2)
    edges = set()
    k = 3
    for i in range(n_nodes):
        for j in np.argsort(d[i])[1:k + 1]:
            edges.add((min(i, int(j)), max(i, int(j))))
    # spanning tree for connectivity (Prim on Euclidean distance)
    inside = np.zeros(n_nodes, dtype=bool)
    inside[0] = True
    best_d = d[0].copy()
    best_p = np.zeros(n_nodes, dtype=int)
    for _ in range(n_nodes - 1):
        cand = np.where(inside, np.inf, best_d)
        j = int(np.argmin(cand))
        i = int(best_p[j])
        edges.add((min(i, j), max(i, j)))
        inside[j] = True
        closer = d[j] < best_d
        best_d = np.where(closer, d[j], best_d)
        best_p = np.where(closer, j, best_p)
    arcs = []
    for idx, (i, j) in enumerate(sorted(edges)):
        tau = max(1, int(math.ceil(d[i, j] / 0.4)))
        cap = int(rng.integers(5, 31))
        arcs.append((i, j, tau, cap, "r%d" % idx))
        arcs.append((j, i, tau, cap, "r%d" % idx))
    perm = rng.permutation(n_nodes)
    onodes, snodes = perm[:n_orig], perm[n_orig:n_orig + n_shel]
    origins = []
    for a, v in enumerate(onodes):
        pop = int(rng.integers(40, 401))
        vul = int(round(pop * rng.uniform(0.10, 0.35)))
        zones = {"Z"} if (a % 2 == 0 or not two_zones) else {"Z2"}
        origins.append({"id": "O%d" % (a + 1), "node": int(v), "pop": pop, "vul": vul,
                        "zones": zones})
    shelters = []
    for s, v in enumerate(snodes):
        school = rng.random() < 0.55
        sh = {"id": "H%d" % (s + 1), "node": int(v), "kind": "school" if school else "ec",
              "cap_ec": 0, "cap_open": 0, "rooms": 0, "q": em.Q_CLASSROOM,
              "accessible": bool(rng.random() < 0.8),
              "zones": {"Z2"} if (two_zones and rng.random() < 0.15) else set(),
              "learners_per_room": int(rng.integers(30, 46))}
        if school:
            sh["cap_open"] = 0 if rng.random() < 0.3 else int(rng.integers(20, 151))
            sh["rooms"] = int(rng.integers(2, 16))
        else:
            sh["cap_ec"] = int(rng.integers(50, 301))
        shelters.append(sh)
    if theta is None:
        theta = int(rng.integers(25, 80))
    return em.Instance(range(n_nodes), arcs, origins, shelters, theta_max=theta)


def random_siting_instance(rng, n_orig=8, n_cand=10):
    """Coverage-structured instance: candidate j reaches a random set of origins
    in one step; every other trip is long. Built on the same road-graph code."""
    nodes = list(range(n_orig + n_cand + 1))
    arcs = []
    far = 1000
    for v in range(len(nodes) - 1):
        arcs.append((v, v + 1, far, 10 ** 6, "f%d" % v))
        arcs.append((v + 1, v, far, 10 ** 6, "f%d" % v))
    origins = [{"id": "O%d" % (a + 1), "node": a, "pop": int(rng.integers(50, 201)),
                "vul": 0, "zones": {"Z"}} for a in range(n_orig)]
    caps = []
    for j in range(n_cand):
        node = n_orig + j
        size = int(rng.integers(2, 5))
        cover = rng.choice(n_orig, size=size, replace=False)
        for a in cover:
            arcs.append((int(a), node, 1, 10 ** 6, "c%d_%d" % (j, a)))
            arcs.append((node, int(a), 1, 10 ** 6, "c%d_%d" % (j, a)))
        tot = sum(origins[int(a)]["pop"] for a in cover)
        caps.append(int(tot * rng.uniform(0.6, 1.0)))
    hnode = n_orig + n_cand
    for a in rng.choice(n_orig, size=2, replace=False):
        arcs.append((int(a), hnode, 1, 10 ** 6, "h%d" % a))
        arcs.append((hnode, int(a), 1, 10 ** 6, "h%d" % a))
    shelters = [{"id": "H1", "node": hnode, "kind": "ec", "cap_ec": int(rng.integers(50, 150)),
                 "cap_open": 0, "rooms": 0, "q": em.Q_CLASSROOM, "accessible": True,
                 "zones": set(), "learners_per_room": 0}]
    inst = em.Instance(nodes, arcs, origins, shelters, theta_max=10 ** 6)
    return inst, [n_orig + j for j in range(n_cand)], caps


# ---------------------------------------------------------------------------
# Independent references
# ---------------------------------------------------------------------------

def lex_lp_reference(inst, scen):
    """Five sequential linear programs (HiGHS), one per lexicographic level."""
    T = em.travel_times(inst, scen)
    sl = em.slots(inst, scen)
    pairs = []
    amounts = {}
    for a, o in enumerate(inst.origins):
        d, v = scen.demand(o), scen.vulnerable(o)
        for cls, vul, amt in (("V", True, v), ("N", False, d - v)):
            if amt <= 0:
                continue
            amounts[(a, cls)] = amt
            for k, slot in enumerate(sl):
                if em.suitable(inst, scen, T, a, slot, vul):
                    pairs.append((a, cls, k))
    if not pairs:
        return (0, 0, 0, 0, 0)
    n = len(pairs)
    rows, rhs = [], []
    for key, amt in amounts.items():
        rows.append([1.0 if (p[0], p[1]) == key else 0.0 for p in pairs])
        rhs.append(amt)
    for k, slot in enumerate(sl):
        rows.append([1.0 if p[2] == k else 0.0 for p in pairs])
        rhs.append(slot[2])
    A = np.array(rows)
    b = np.array(rhs, dtype=float)
    w_v = np.array([1.0 if p[1] == "V" else 0.0 for p in pairs])
    w_all = np.ones(n)
    w_room = np.array([1.0 if sl[p[2]][1] == em.TIER_ROOM else 0.0 for p in pairs])
    w_open = np.array([1.0 if sl[p[2]][1] == em.TIER_OPEN else 0.0 for p in pairs])
    w_time = np.array([float(T[p[0]][sl[p[2]][0]]) for p in pairs])
    stages = [(-w_v, True), (-w_all, True), (w_room, False), (w_open, False), (w_time, False)]
    values = []
    A_cur, b_cur = A, b
    for c, is_max in stages:
        res = linprog(c, A_ub=A_cur, b_ub=b_cur, bounds=(0, None), method="highs")
        assert res.status == 0, res.message
        z = res.fun
        values.append(-z if is_max else z)
        A_cur = np.vstack([A_cur, c])
        b_cur = np.append(b_cur, z + 1e-7 * max(1.0, abs(z)))
    return tuple(int(round(v)) for v in values)


def exact_classrooms_milp(inst, scen, fv, ftot):
    """Fewest classrooms closed over all plans that place fv vulnerable and ftot in all."""
    T = em.travel_times(inst, scen)
    sl = em.slots(inst, scen)
    pairs, amounts = [], {}
    for a, o in enumerate(inst.origins):
        d, v = scen.demand(o), scen.vulnerable(o)
        for cls, vul, amt in (("V", True, v), ("N", False, d - v)):
            if amt <= 0:
                continue
            amounts[(a, cls)] = amt
            for k, slot in enumerate(sl):
                if em.suitable(inst, scen, T, a, slot, vul):
                    pairs.append((a, cls, k))
    room_slots = [k for k, slot in enumerate(sl) if slot[1] == em.TIER_ROOM]
    n, m = len(pairs), len(room_slots)
    nv = n + m
    cons = []
    for key, amt in amounts.items():
        row = np.zeros(nv)
        for i, p in enumerate(pairs):
            if (p[0], p[1]) == key:
                row[i] = 1
        cons.append(LinearConstraint(row, -np.inf, amt))
    for k, slot in enumerate(sl):
        row = np.zeros(nv)
        for i, p in enumerate(pairs):
            if p[2] == k:
                row[i] = 1
        cons.append(LinearConstraint(row, -np.inf, slot[2]))
    for r, k in enumerate(room_slots):
        row = np.zeros(nv)
        for i, p in enumerate(pairs):
            if p[2] == k:
                row[i] = 1
        row[n + r] = -inst.shelters[sl[k][0]]["q"]
        cons.append(LinearConstraint(row, -np.inf, 0))
    row = np.zeros(nv)
    for i, p in enumerate(pairs):
        if p[1] == "V":
            row[i] = 1
    cons.append(LinearConstraint(row, fv, fv))
    row = np.zeros(nv)
    row[:n] = 1
    cons.append(LinearConstraint(row, ftot, ftot))
    c = np.zeros(nv)
    c[n:] = 1
    integrality = np.zeros(nv)
    integrality[n:] = 1
    ub = np.full(nv, np.inf)
    for r, k in enumerate(room_slots):
        ub[n + r] = inst.shelters[sl[k][0]]["rooms"]
    res = milp(c, constraints=cons, integrality=integrality, bounds=Bounds(np.zeros(nv), ub))
    assert res.status == 0, res.message
    return int(round(res.fun))


def ford_fulkerson_value(inst, scen, s, t, horizon):
    """max over static flows f of (T+1)|f| - sum tau_e f_e  (linear program)."""
    arcs = inst.open_arcs(scen.closed_tags)
    nodes = inst.nodes
    idx = {v: i for i, v in enumerate(nodes)}
    m = len(arcs)
    # variables: f_e (m) then v
    c = np.zeros(m + 1)
    for e, (u, w, tau, cap, tag) in enumerate(arcs):
        c[e] = tau
    c[m] = -(horizon + 1)
    A_eq = np.zeros((len(nodes), m + 1))
    for e, (u, w, tau, cap, tag) in enumerate(arcs):
        A_eq[idx[u], e] += 1
        A_eq[idx[w], e] -= 1
    A_eq[idx[s], m] = -1
    A_eq[idx[t], m] = 1
    bounds = [(0, a[3]) for a in arcs] + [(0, None)]
    res = linprog(c, A_eq=A_eq, b_eq=np.zeros(len(nodes)), bounds=bounds, method="highs")
    assert res.status == 0, res.message
    return int(round(-res.fun))


def clearance_linear_scan(inst, scen, supplies, caps):
    total = sum(supplies.values())
    t = 0
    while em.arrivals_by(inst, scen, t, supplies, caps) < total:
        t += 1
    return t


# ---------------------------------------------------------------------------
# Verification suite
# ---------------------------------------------------------------------------

def run_verification(rng):
    out = {}
    scen = em.Scenario("Z+Z2", {"Z", "Z2"})

    # V1: lexicographic plan against five sequential LPs ------------------
    n_inst, agree, levels_checked, nonint = 0, 0, 0, 0
    classroom_cases = []
    for _ in range(300):
        inst = random_instance(rng, n_nodes=int(rng.integers(14, 27)),
                               n_orig=int(rng.integers(3, 8)), n_shel=int(rng.integers(3, 9)))
        plan = em.lex_plan(inst, scen, "lex")
        ref = lex_lp_reference(inst, scen)
        mine = (plan["vul_placed"], plan["placed"], plan["persons_room"],
                plan["persons_open"], plan["person_minutes"])
        n_inst += 1
        levels_checked += 5
        if mine == ref:
            agree += 1
        if any(int(f) != f for f in plan["x"].values()):
            nonint += 1
        if plan["persons_room"] > 0:
            classroom_cases.append((inst, plan))
    out["V1"] = {"instances": n_inst, "agree": agree, "levels": levels_checked,
                 "nonintegral": nonint}

    # V2: classroom packing bound against an exact mixed-integer program ---
    gaps, viol, cases = [], 0, 0
    exact_hits = 0
    m_values = []
    for inst, plan in classroom_cases[:150]:
        kstar = exact_classrooms_milp(inst, scen, plan["vul_placed"], plan["placed"])
        ours = plan["rooms_closed_total"]
        msch = len(plan["rooms_closed"])
        cases += 1
        g = ours - kstar
        gaps.append(g)
        m_values.append(msch)
        if g < 0 or g > msch - 1:
            viol += 1
        if g == 0:
            exact_hits += 1
    out["V2"] = {"cases": cases, "violations": viol, "exact": exact_hits,
                 "gap_max": max(gaps) if gaps else 0,
                 "gap_mean": float(np.mean(gaps)) if gaps else 0.0,
                 "gap_hist": {str(k): gaps.count(k) for k in sorted(set(gaps))},
                 "schools_used_max": max(m_values) if m_values else 0}

    # V3: time-expanded max flow against the Ford-Fulkerson formula --------
    pairs_checked, agree3, nonzero = 0, 0, 0
    for _ in range(60):
        inst = random_instance(rng, n_nodes=int(rng.integers(10, 19)), n_orig=1, n_shel=1)
        s = inst.origins[0]["node"]
        t = inst.shelters[0]["node"]
        sc = em.Scenario("none", set())
        for horizon in range(0, 61, 6):
            big = 10 ** 9
            te = em.arrivals_by(inst, sc, horizon, {s: big}, {t: None})
            ff = ford_fulkerson_value(inst, sc, s, t, horizon)
            pairs_checked += 1
            agree3 += int(te == ff)
            nonzero += int(te > 0)
    out["V3"] = {"pairs": pairs_checked, "agree": agree3, "nonzero": nonzero}

    # V4: clearance time by bisection against a linear scan; lower bound ---
    agree4, n4, lb_viol, ratios, calls_l, scan_l = 0, 0, 0, [], [], []
    for _ in range(80):
        inst = random_instance(rng, n_nodes=int(rng.integers(10, 17)),
                               n_orig=int(rng.integers(2, 5)), n_shel=int(rng.integers(2, 5)))
        plan = em.lex_plan(inst, scen, "lex")
        sup, caps = em.plan_supplies(inst, plan)
        if sum(sup.values()) == 0:
            continue
        tb, calls = em.clearance_time(inst, scen, sup, caps)
        tl = clearance_linear_scan(inst, scen, sup, caps)
        lb = em.clearance_lower_bound(inst, scen, sup, caps)
        n4 += 1
        agree4 += int(tb == tl)
        lb_viol += int(lb > tb)
        ratios.append(lb / tb if tb > 0 else 1.0)
        calls_l.append(calls)
        scan_l.append(tl + 1)
    out["V4"] = {"instances": n4, "agree": agree4, "lb_violations": lb_viol,
                 "lb_ratio_mean": float(np.mean(ratios)), "lb_ratio_min": float(np.min(ratios)),
                 "bisection_calls_mean": float(np.mean(calls_l)),
                 "scan_calls_mean": float(np.mean(scan_l))}

    # V5: monotonicity under closures and added shelters -------------------
    checks, viol5 = {"closure_time": 0, "closure_rooms": 0, "add_rooms": 0,
                     "add_time": 0, "alert": 0}, {"closure_time": 0, "closure_rooms": 0,
                                                   "add_rooms": 0, "add_time": 0, "alert": 0}
    for _ in range(120):
        inst = random_instance(rng, n_nodes=int(rng.integers(10, 17)),
                               n_orig=int(rng.integers(2, 6)), n_shel=int(rng.integers(2, 6)))
        base = em.lex_plan(inst, scen, "lex")
        sup, caps = em.plan_supplies(inst, base)
        tags = sorted({a[4] for a in inst.arcs})
        tag = tags[int(rng.integers(0, len(tags)))]
        closed = em.Scenario("closed", scen.zones, closed_tags=(tag,))
        if sum(sup.values()) > 0:
            t0, _ = em.clearance_time(inst, scen, sup, caps)
            t1, _ = em.clearance_time(inst, closed, sup, caps)
            checks["closure_time"] += 1
            viol5["closure_time"] += int(t1 < t0)
        after = em.lex_plan(inst, closed, "lex")
        if after["vul_placed"] == base["vul_placed"] and after["placed"] == base["placed"]:
            checks["closure_rooms"] += 1
            viol5["closure_rooms"] += int(after["persons_room"] < base["persons_room"])
        # add a non-school shelter at a random node
        node = int(rng.integers(0, len(inst.nodes)))
        extra = dict(inst.shelters[0])
        extra.update({"id": "NEW", "node": node, "kind": "ec", "cap_ec": int(rng.integers(30, 200)),
                      "cap_open": 0, "rooms": 0, "zones": set(), "accessible": True})
        inst2 = em.Instance(inst.nodes, inst.arcs, inst.origins, inst.shelters + [extra],
                            theta_max=inst.theta_max)
        added = em.lex_plan(inst2, scen, "lex")
        if added["vul_placed"] == base["vul_placed"] and added["placed"] == base["placed"]:
            checks["add_rooms"] += 1
            viol5["add_rooms"] += int(added["persons_room"] > base["persons_room"])
        if sum(sup.values()) > 0:
            caps2 = dict(caps)
            caps2[node] = caps2.get(node, 0) + extra["cap_ec"]
            t2, _ = em.clearance_time(inst2, scen, sup, caps2)
            t0b, _ = em.clearance_time(inst, scen, sup, caps)
            checks["add_time"] += 1
            viol5["add_time"] += int(t2 > t0b)
        # alert-level nesting: zone Z only versus Z and Z2 with a closure
        small = em.Scenario("Z", {"Z"})
        big = em.Scenario("Z+Z2 closed", {"Z", "Z2"}, closed_tags=(tag,))
        p_small, p_big = em.lex_plan(inst, small, "lex"), em.lex_plan(inst, big, "lex")
        if p_big["placed"] == p_big["demand"]:
            checks["alert"] += 1
            viol5["alert"] += int(p_small["persons_room"] > p_big["persons_room"])
    out["V5"] = {"checks": checks, "violations": viol5}

    # V6 and V7: submodularity of coverage; greedy against exhaustive -----
    sub_checks, sub_viol = {"road": 0, "coverage": 0}, {"road": 0, "coverage": 0}
    ratios7 = {1: [], 2: [], 3: [], 4: []}
    for rep in range(80):
        if rep % 2 == 0:
            kind = "road"
            inst = random_instance(rng, n_nodes=int(rng.integers(16, 25)),
                                   n_orig=int(rng.integers(4, 8)), n_shel=int(rng.integers(2, 5)),
                                   two_zones=False)
            cand_nodes = [int(v) for v in rng.choice(len(inst.nodes), size=10, replace=False)]
            cand_cap = [int(rng.integers(40, 250)) for _ in cand_nodes]
            theta = int(rng.integers(15, 45))
        else:
            kind = "coverage"
            inst, cand_nodes, cand_cap = random_siting_instance(rng)
            theta = 1
        sc = em.Scenario("Z", {"Z"})
        prob = em.SitingProblem(inst, sc, theta, cand_nodes, cand_cap)
        J = list(range(len(cand_nodes)))
        for _ in range(60):
            Tset = [j for j in J if rng.random() < 0.5]
            Sset = [j for j in Tset if rng.random() < 0.5]
            rest = [j for j in J if j not in Tset]
            if not rest:
                continue
            j = rest[int(rng.integers(0, len(rest)))]
            lhs = prob.gain(Sset + [j]) - prob.gain(Sset)
            rhs = prob.gain(Tset + [j]) - prob.gain(Tset)
            sub_checks[kind] += 1
            sub_viol[kind] += int(lhs < rhs)
        for k in (1, 2, 3, 4):
            _, g = em.greedy_sites(prob, k)
            _, b = em.best_sites(prob, k)
            if b > 0:
                ratios7[k].append(g / b)
    allr = [r for k in ratios7 for r in ratios7[k]]
    out["V6"] = {"checks": sub_checks, "violations": sub_viol,
                 "checks_total": sum(sub_checks.values()),
                 "violations_total": sum(sub_viol.values())}
    out["V7"] = {"instances": len(allr), "ratio_min": float(np.min(allr)),
                 "ratio_mean": float(np.mean(allr)),
                 "share_optimal": float(np.mean([r >= 1 - 1e-12 for r in allr])),
                 "by_k": {str(k): {"n": len(v), "min": float(np.min(v)), "mean": float(np.mean(v))}
                          for k, v in ratios7.items() if v}}
    return out


# ---------------------------------------------------------------------------
# Computational cost
# ---------------------------------------------------------------------------

def run_timing(rng, repeats=5):
    """Wall-clock time; each figure is the fastest of `repeats` runs."""
    rows = []
    scen = em.Scenario("Z", {"Z", "Z2"})
    for n_nodes, n_orig, n_shel in ((100, 20, 15), (200, 40, 30), (400, 80, 60), (800, 160, 120)):
        inst = random_instance(rng, n_nodes=n_nodes, n_orig=n_orig, n_shel=n_shel, theta=10 ** 6)
        best = math.inf
        for _ in range(repeats):
            t0 = time.perf_counter()
            plan = em.lex_plan(inst, scen, "lex")
            best = min(best, time.perf_counter() - t0)
        rows.append({"nodes": n_nodes, "origins": n_orig, "shelters": n_shel,
                     "arcs": len(inst.arcs), "demand": plan["demand"], "seconds": best})
    rows_te = []
    inst = random_instance(rng, n_nodes=40, n_orig=6, n_shel=6, theta=10 ** 6)
    plan = em.lex_plan(inst, scen, "lex")
    sup, caps = em.plan_supplies(inst, plan)
    for horizon in (30, 60, 120, 240):
        G = em.expanded_network(inst, scen, horizon, sup, caps)
        best = math.inf
        for _ in range(repeats):
            t0 = time.perf_counter()
            em.arrivals_by(inst, scen, horizon, sup, caps)
            best = min(best, time.perf_counter() - t0)
        rows_te.append({"horizon": horizon, "vertices": G.number_of_nodes(),
                        "arcs": G.number_of_edges(), "seconds": best})
    return {"plan": rows, "expanded": rows_te}


# ---------------------------------------------------------------------------
# Worked instance E1 (synthetic volcano)
# ---------------------------------------------------------------------------

def polar(r, deg):
    t = math.radians(deg)
    return (r * math.cos(t), r * math.sin(t))


CHANNELS = {"A": 312.0, "B": 248.0}      # lahar channel bearings (degrees)


def _crosses(p, q, deg, r0=1.0, r1=16.0):
    """Does road segment p-q cross the channel ray at bearing deg?"""
    dx, dy = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    ex, ey = q[0] - p[0], q[1] - p[1]
    det = ex * (-dy) - ey * (-dx)
    if abs(det) < 1e-12:
        return False
    # p + t e = s d
    t = ((0 - p[0]) * (-dy) - (0 - p[1]) * (-dx)) / det
    sr = (ex * (0 - p[1]) - ey * (0 - p[0])) / det
    return 0.0 < t < 1.0 and r0 <= sr <= r1


def build_e1():
    pos = {}
    for k in range(12):
        pos["R%d" % k] = polar(8.0, 30 * k)
    towns = {"TE": (12.0, 0), "TNE": (13.0, 45), "TSE": (13.0, 325), "TS": (11.0, 275),
             "TSW": (12.0, 220)}
    for t, (r, a) in towns.items():
        pos[t] = polar(r, a)
    origins_def = [("O1", 4.6, 80, 520, 114, {"PDZ"}, ["R3", "R2"]),
                   ("O2", 5.4, 20, 430, 82, {"PDZ"}, ["R1", "R0"]),
                   ("O3", 5.6, 300, 610, 146, {"PDZ"}, ["R10", "R11"]),
                   ("O4", 6.6, 262, 380, 80, {"EDZ"}, ["R9", "R8"]),
                   ("O5", 6.8, 228, 450, 90, {"EDZ"}, ["R8", "R7"]),
                   ("O6", 9.4, 318, 300, 75, {"LAHAR"}, ["R11", "TSE"])]
    for oid, r, a, *_ in origins_def:
        pos[oid] = polar(r, a)
    arcs = []
    bridges = {}

    def road(u, v, speed, cap, tag):
        dist = math.dist(pos[u], pos[v])
        tau = max(1, int(math.ceil(dist / speed)))
        for ch, deg in CHANNELS.items():
            if _crosses(pos[u], pos[v], deg):
                n = sum(1 for b in bridges.values() if b == ch) + 1
                tag = "%s%d" % (ch, n)
                bridges[tag] = ch
                break
        arcs.append((u, v, tau, cap, tag))
        arcs.append((v, u, tau, cap, tag))

    for k in range(12):
        road("R%d" % k, "R%d" % ((k + 1) % 12), 0.5, 30, "ring%d" % k)
    road("TE", "R0", 0.5, 40, "hTE")
    road("TNE", "R1", 0.5, 40, "hTNE1")
    road("TNE", "R2", 0.5, 40, "hTNE2")
    road("TSE", "R10", 0.5, 40, "hTSE1")
    road("TSE", "R11", 0.5, 40, "hTSE2")
    road("TS", "R9", 0.5, 40, "hTS")
    road("TSW", "R7", 0.5, 40, "hTSW1")
    road("TSW", "R8", 0.5, 40, "hTSW2")
    road("TE", "TSE", 0.5, 30, "oE")
    road("TSE", "TS", 0.5, 30, "oSE")
    road("TS", "TSW", 0.5, 30, "oS")
    road("TE", "TNE", 0.5, 30, "oN")
    origins = []
    for oid, r, a, pop, vul, zones, links in origins_def:
        for w in links:
            road(oid, w, 0.25, 20, "b" + oid + w)
        origins.append({"id": oid, "node": oid, "pop": pop, "vul": vul, "zones": zones})
    q = em.Q_CLASSROOM
    shelters = [
        {"id": "EC1", "name": "Municipal evacuation center", "node": "TE", "kind": "ec",
         "cap_ec": em.capacity_from_area(1400), "cap_open": 0, "rooms": 0, "q": q,
         "accessible": True, "zones": set(), "learners_per_room": 0, "area": 1400},
        {"id": "EC2", "name": "Parish hall", "node": "TSE", "kind": "ec",
         "cap_ec": em.capacity_from_area(700), "cap_open": 0, "rooms": 0, "q": q,
         "accessible": True, "zones": set(), "learners_per_room": 0, "area": 700},
        {"id": "EC3", "name": "Barangay covered court", "node": "TSW", "kind": "ec",
         "cap_ec": em.capacity_from_area(1050), "cap_open": 0, "rooms": 0, "q": q,
         "accessible": True, "zones": set(), "learners_per_room": 0, "area": 1050},
        {"id": "SCH1", "name": "Central elementary school", "node": "TS", "kind": "school",
         "cap_ec": 0, "cap_open": em.capacity_from_area(630), "rooms": 20, "q": q,
         "accessible": True, "zones": set(), "learners_per_room": 40, "area": 630},
        {"id": "SCH2", "name": "National high school", "node": "TSE", "kind": "school",
         "cap_ec": 0, "cap_open": em.capacity_from_area(840), "rooms": 30, "q": q,
         "accessible": True, "zones": set(), "learners_per_room": 45, "area": 840},
        {"id": "SCH3", "name": "Two-storey elementary school", "node": "TNE", "kind": "school",
         "cap_ec": 0, "cap_open": 0, "rooms": 14, "q": q,
         "accessible": False, "zones": set(), "learners_per_room": 38, "area": 0},
    ]
    nodes = list(pos)
    inst = em.Instance(nodes, arcs, origins, shelters, theta_max=120)
    inst.bridges = bridges
    return inst, pos


ALL_BRIDGES = ("A1", "A2", "A3", "A4", "B1", "B2", "B3")


def e1_scenarios():
    return [em.Scenario("AL3", {"PDZ"}),
            em.Scenario("AL4", {"PDZ", "EDZ"}),
            em.Scenario("AL4+L", {"PDZ", "EDZ", "LAHAR"}, closed_tags=ALL_BRIDGES)]


def run_e1():
    inst, pos = build_e1()
    res = {"origins": [], "shelters": [], "scenarios": {}, "siting": {}}
    base_scen = em.Scenario("open", set())
    T = em.travel_times(inst, base_scen)
    for a, o in enumerate(inst.origins):
        near = min((T[a][s], s) for s in range(len(inst.shelters)))
        res["origins"].append({"id": o["id"], "zone": sorted(o["zones"])[0], "pop": o["pop"],
                               "vul": o["vul"],
                               "dist_km": round(math.dist(pos[o["node"]], (0, 0)), 1),
                               "nearest": inst.shelters[near[1]]["id"], "nearest_min": near[0]})
    for sh in inst.shelters:
        res["shelters"].append({"id": sh["id"], "name": sh["name"], "kind": sh["kind"],
                                "area": sh["area"], "cap_ec": sh["cap_ec"],
                                "cap_open": sh["cap_open"], "rooms": sh["rooms"],
                                "room_cap": sh["rooms"] * sh["q"],
                                "accessible": sh["accessible"],
                                "learners_per_room": sh["learners_per_room"]})
    curves = {}
    for scen in e1_scenarios():
        near = em.nearest_plan(inst, scen)
        blind = em.lex_plan(inst, scen, "blind")
        lex = em.lex_plan(inst, scen, "lex")
        sup, caps = em.plan_supplies(inst, lex)
        tclear, _ = em.clearance_time(inst, scen, sup, caps)
        lb = em.clearance_lower_bound(inst, scen, sup, caps)
        entry = {"demand": lex["demand"], "vulnerable": lex["vulnerable"],
                 "nearest_overflow": near["overflow"],
                 "nearest_person_minutes": near["person_minutes"]}
        for name, p in (("blind", blind), ("lex", lex)):
            entry[name] = {k: p[k] for k in ("vul_placed", "placed", "unplaced", "persons_ec",
                                             "persons_open", "persons_room",
                                             "rooms_closed_total", "learners_displaced",
                                             "person_minutes", "max_time")}
            entry[name]["mean_time"] = round(p["mean_time"], 2)
            entry[name]["rooms_by_school"] = {inst.shelters[s]["id"]: v
                                              for s, v in p["rooms_closed"].items()}
            entry[name]["load"] = {inst.shelters[s]["id"]: v for s, v in p["load"].items()}
        sb, cb = em.plan_supplies(inst, blind)
        tblind, _ = em.clearance_time(inst, scen, sb, cb)
        entry["clearance_lex"] = tclear
        entry["clearance_blind"] = tblind
        entry["clearance_lb"] = lb
        # assignment table for the lexicographic plan
        assign = {}
        for (a, k, cls), f in lex["x"].items():
            s, tier, cap, acc = lex["slots"][k]
            key = (inst.origins[a]["id"], inst.shelters[s]["id"], em.TIER_NAMES[tier])
            assign[key] = assign.get(key, 0) + f
        entry["assignment"] = [{"origin": k[0], "shelter": k[1], "space": k[2], "persons": v}
                               for k, v in sorted(assign.items())]
        res["scenarios"][scen.name] = entry
        horizon = max(tclear, 1) + 10
        curves[scen.name] = [em.arrivals_by(inst, scen, t, sup, caps) for t in range(0, horizon + 1, 2)]
    # bridge closures under AL4: with the AL4 plan held fixed (Proposition 8)
    # and with a fresh plan for the closed network
    al4 = em.Scenario("AL4", {"PDZ", "EDZ"})
    lex4 = em.lex_plan(inst, al4, "lex")
    sup, caps = em.plan_supplies(inst, lex4)
    t_open, _ = em.clearance_time(inst, al4, sup, caps)
    per_bridge = {}
    for b in ALL_BRIDGES:
        sc = em.Scenario("AL4-" + b, {"PDZ", "EDZ"}, closed_tags=(b,))
        tb, _ = em.clearance_time(inst, sc, sup, caps)
        per_bridge[b] = tb
    res["bridge_single"] = {"open": t_open, "closed": per_bridge}
    groups = {"none": (), "A": tuple(b for b in ALL_BRIDGES if b.startswith("A")),
              "B": tuple(b for b in ALL_BRIDGES if b.startswith("B")), "A+B": ALL_BRIDGES}
    rows = {}
    for name, tags in groups.items():
        sc = em.Scenario("AL4 closed " + name, {"PDZ", "EDZ"}, closed_tags=tags)
        tfix, _ = em.clearance_time(inst, sc, sup, caps)
        p = em.lex_plan(inst, sc, "lex")
        s2, c2 = em.plan_supplies(inst, p)
        tnew, _ = em.clearance_time(inst, sc, s2, c2)
        rows[name] = {"bridges": list(tags), "clearance_fixed_plan": tfix,
                      "unplaced": p["unplaced"], "persons_room": p["persons_room"],
                      "rooms_closed": p["rooms_closed_total"], "clearance_new_plan": tnew,
                      "mean_time": round(p["mean_time"], 2), "max_time": p["max_time"]}
    res["channel_closures"] = rows
    # siting new evacuation centers for AL4+L
    scen = e1_scenarios()[2]
    cands = ["TS", "TSW", "TNE", "TE", "TSE"]
    area_new = [1400, 1050, 1225, 1050, 875]
    cap_new = [em.capacity_from_area(a) for a in area_new]
    prob = em.SitingProblem(inst, scen, THETA_SITE, cands, cap_new)
    order, _ = em.greedy_sites(prob, 3)
    greedy_rows = []
    for k in (1, 2, 3):
        S = order[:k]
        gk = prob.gain(S)
        bS, bk = em.best_sites(prob, k)
        extra = list(inst.shelters)
        for j in S:
            extra.append({"id": "LPC-" + cands[j], "name": "Ligtas Pinoy Center", "node": cands[j],
                          "kind": "ec", "cap_ec": cap_new[j], "cap_open": 0, "rooms": 0,
                          "q": em.Q_CLASSROOM, "accessible": True, "zones": set(),
                          "learners_per_room": 0, "area": area_new[j]})
        inst2 = em.Instance(inst.nodes, inst.arcs, inst.origins, extra, theta_max=inst.theta_max)
        p2 = em.lex_plan(inst2, scen, "lex")
        s2, c2 = em.plan_supplies(inst2, p2)
        t2, _ = em.clearance_time(inst2, scen, s2, c2)
        greedy_rows.append({"k": k, "sites": [cands[j] for j in S], "gain": gk,
                            "best_sites": [cands[j] for j in bS], "best_gain": bk,
                            "unplaced": p2["unplaced"], "persons_room": p2["persons_room"],
                            "rooms_closed": p2["rooms_closed_total"],
                            "learners": p2["learners_displaced"], "clearance": t2})
    res["siting"] = {"theta": THETA_SITE, "candidates": cands, "capacity": cap_new,
                     "area": area_new,
                     "phi0": prob.phi0, "rows": greedy_rows,
                     "single_gains": {cands[j]: prob.gain([j]) for j in range(len(cands))}}
    res["curves"] = curves
    res["pos"] = {k: [round(v[0], 3), round(v[1], 3)] for k, v in pos.items()}
    res["arcs"] = [[u, v, tau, cap, tag] for (u, v, tau, cap, tag) in inst.arcs]
    return res


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

def figures(e1):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "serif", "font.serif": ["Liberation Serif", "Times New Roman"],
                         "font.size": 10})
    pos = {k: tuple(v) for k, v in e1["pos"].items()}
    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    ax.add_patch(plt.Circle((0, 0), 6.0, color="#C0392B", alpha=0.10, lw=0))
    ax.add_patch(plt.Circle((0, 0), 6.0, fill=False, color="#C0392B", lw=1.2, ls="--"))
    import matplotlib.patches as mp
    ax.add_patch(mp.Wedge((0, 0), 7.0, 200, 340, width=1.0, color="#E67E22", alpha=0.18, lw=0))
    for ang in CHANNELS.values():
        x1, y1 = polar(2.0, ang)
        x2, y2 = polar(15.0, ang)
        ax.plot([x1, x2], [y1, y2], color="#8E6E53", lw=3, alpha=0.35, solid_capstyle="round")
    drawn = set()
    for u, v, tau, cap, tag in e1["arcs"]:
        key = tuple(sorted((u, v)))
        if key in drawn:
            continue
        drawn.add(key)
        x = [pos[u][0], pos[v][0]]
        y = [pos[u][1], pos[v][1]]
        if tag in ALL_BRIDGES:
            ax.plot(x, y, color="#7F8C8D", lw=1.8)
            mx, my = (x[0] + x[1]) / 2, (y[0] + y[1]) / 2
            ax.plot(mx, my, marker="s", color="#8E6E53", ms=7)
            off = {"A1": (7, 2), "A2": (6, -12), "A3": (6, -12), "A4": (-20, 6),
                   "B1": (6, -12), "B2": (6, -12), "B3": (-22, 2)}[tag]
            ax.annotate(tag, (mx, my), textcoords="offset points", xytext=off, fontsize=8)
        elif tag.startswith("b"):
            ax.plot(x, y, color="#95A5A6", lw=1.0, ls=":")
        else:
            ax.plot(x, y, color="#7F8C8D", lw=1.8 if cap >= 40 else 1.0)
    ax.plot(0, 0, marker="^", color="#2C3E50", ms=12)
    ax.annotate("summit", (0, 0), textcoords="offset points", xytext=(6, 4), fontsize=8)
    for o in e1["origins"]:
        p = pos[o["id"]]
        ax.plot(*p, marker="o", color="#C0392B", ms=8, mec="white")
        ax.annotate(o["id"], p, textcoords="offset points", xytext=(5, 5), fontsize=9, weight="bold")
    shel_at = {}
    for sh in e1["shelters"]:
        node = {"EC1": "TE", "EC2": "TSE", "EC3": "TSW", "SCH1": "TS", "SCH2": "TSE",
                "SCH3": "TNE"}[sh["id"]]
        shel_at.setdefault(node, []).append(sh["id"])
    for node, ids in shel_at.items():
        p = pos[node]
        ax.plot(*p, marker="s", color="#1F618D", ms=9, mec="white")
        ax.annotate(", ".join(ids), p, textcoords="offset points", xytext=(6, 6), fontsize=8,
                    color="#1F618D")
    for k in range(12):
        ax.plot(*pos["R%d" % k], marker=".", color="#555555", ms=4)
    ax.set_aspect("equal")
    ax.set_xlim(-15, 15)
    ax.set_ylim(-15, 15)
    ax.set_xlabel("km east of the summit")
    ax.set_ylabel("km north of the summit")
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], marker="o", color="#C0392B", ls="", label="origin (barangay cluster)"),
               Line2D([], [], marker="s", color="#1F618D", ls="", label="shelter"),
               Line2D([], [], marker="s", color="#8E6E53", ls="", label="bridge over lahar channel"),
               mp.Patch(color="#C0392B", alpha=0.25, label="6-km permanent danger zone"),
               mp.Patch(color="#E67E22", alpha=0.35, label="extended danger zone (7 km)")]
    ax.legend(handles=handles, loc="lower left", fontsize=7.5, frameon=True)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig_e1_map.png"), dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    colors = {"AL3": "#1F618D", "AL4": "#C0392B", "AL4+L": "#8E6E53"}
    styles = {"AL3": "-", "AL4": "--", "AL4+L": "-."}
    for name, ys in e1["curves"].items():
        xs = list(range(0, 2 * len(ys), 2))
        ax.plot(xs, ys, styles[name], color=colors[name], lw=1.8, label=name)
    ax.set_xlabel("minutes after the evacuation order")
    ax.set_ylabel("evacuees in shelters, F(T)")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig_e1_arrivals.png"), dpi=220)
    plt.close(fig)


def main():
    rng = np.random.default_rng(SEED)
    t0 = time.time()
    results = {"seed": SEED}
    results["verification"] = run_verification(rng)
    print("verification done", round(time.time() - t0, 1), "s", flush=True)
    results["timing"] = run_timing(rng)
    print("timing done", round(time.time() - t0, 1), "s", flush=True)
    results["e1"] = run_e1()
    print("E1 done", round(time.time() - t0, 1), "s", flush=True)
    figures(results["e1"])
    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(results, f, indent=1, default=str)
    print(json.dumps(results["verification"], indent=1))


if __name__ == "__main__":
    main()
