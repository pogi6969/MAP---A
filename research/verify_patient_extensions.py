#!/usr/bin/env python3
"""Synthetic checks for the patient-needs and hospital-mapping parts of the revised paper.

Every figure in Tables 24 to 33 of the revised paper is printed by this script.
Inputs are random instances made here with a fixed seed, plus the published
travel times and hospital attributes of instance S1 (Tables 16 and 20).
No real hospital, road, timetable, or mailbox is used.

Run:  python3 verify_patient_extensions.py  > results.txt
Needs numpy and scipy.
"""
import bisect
import heapq
import itertools
import json
import math
import random
import time

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.spatial import cKDTree

SEED = 20261013
INF = float("inf")

# Service codes; the default service set of each level follows Table 5 (DOH, 2012).
SERVICES = ["ISO", "MAT", "OR", "ICU", "NICU", "HRP", "DIA", "BB"]
LEVEL_SERVICES = {
    0: frozenset(),
    1: frozenset({"ISO", "MAT", "OR"}),
    2: frozenset({"ISO", "MAT", "OR", "ICU", "NICU", "HRP"}),
    3: frozenset(SERVICES),
}
LAMBDA = {1: 3, 2: 2, 3: 1, 4: 1, 5: 0}   # Table 9
KE = {1, 2}
RHO_MAX = 3


# ---------------------------------------------------------------- suitability
def suitable(h, p):
    """Equation (15) extended with the need factor of Definition 21."""
    k = p["kappa"]
    if h["level"] < LAMBDA[k]:
        return False
    if not p["needs"] <= h["services"]:
        return False
    if k in KE and not h["er"]:
        return False
    if h["status"] == "FULL":
        return False
    if k not in KE and h["q"] > p["rho"]:
        return False
    return True


def tie_key(d, h):
    b = h["b"] if h["status"] == "AVAILABLE" else 0
    return (d, -b, h["id"])


# ---------------------------------------------------------------- road graphs
def road_graph(rng, n, k_near=3, closed_share=0.2):
    side = math.sqrt(n) * 0.5
    pts = np.array([(rng.random() * side, rng.random() * side) for _ in range(n)])
    tree = cKDTree(pts)
    _, nb = tree.query(pts, k=k_near + 1)
    segs = {}
    for u in range(n):
        for v in nb[u][1:]:
            v = int(v)
            a, b = (u, v) if u < v else (v, u)
            if (a, b) in segs:
                continue
            km = float(np.linalg.norm(pts[a] - pts[b])) * 1.25
            speed = rng.choice([20.0, 30.0, 40.0, 60.0])
            minutes = km / speed * 60.0 + 1e-6 * rng.random()
            segs[(a, b)] = (minutes, rng.random() >= closed_share)
    return pts, segs


def adjacency(n, segs, skip=None):
    fwd = [[] for _ in range(n)]
    for (a, b), (w, is_open) in segs.items():
        if not is_open or (a, b) == skip:
            continue
        fwd[a].append((b, w))
        fwd[b].append((a, w))
    return fwd   # roads are two-way, so the reversed graph is the same


def random_hospitals(rng, n_nodes, count, ids_from=0):
    nodes = rng.sample(range(n_nodes), count)
    hs = []
    for i, v in enumerate(nodes):
        level = rng.choice([0, 1, 1, 2, 2, 3])
        services = set(LEVEL_SERVICES[level])
        # registers sometimes list a service above or below the level default
        for s in SERVICES:
            if rng.random() < 0.08:
                services ^= {s}
        status = rng.choice(["AVAILABLE", "AVAILABLE", "AVAILABLE", "FULL", "UNKNOWN"])
        hs.append({
            "id": ids_from + i, "node": v, "level": level, "services": frozenset(services),
            "er": rng.random() < 0.8, "q": rng.choice([0, 1, 2, 3]), "status": status,
            "b": rng.randint(1, 12) if status == "AVAILABLE" else 0,
        })
    return hs


def random_profile(rng, need_max=2):
    k = rng.randint(1, 5)
    needs = frozenset(rng.sample(SERVICES, rng.randint(0, need_max)))
    return {"kappa": k, "rho": rng.randint(0, 3), "needs": needs}


def floyd_warshall(n, adj):
    d = np.full((n, n), np.inf)
    np.fill_diagonal(d, 0.0)
    for u in range(n):
        for v, w in adj[u]:
            if w < d[u, v]:
                d[u, v] = w
    for k in range(n):
        d = np.minimum(d, d[:, k:k + 1] + d[k:k + 1, :])
    return d


# ---------------------------------------------------------------- searches
def k_nearest_suitable(adj, src, hosp_at, hospitals, prof, k=1):
    """Early-stopping Dijkstra (Proposition 9 and Corollary 15)."""
    dist = {src: 0.0}
    pq = [(0.0, src)]
    done = set()
    found = []
    bound = None
    while pq:
        d, u = heapq.heappop(pq)
        if u in done:
            continue
        if bound is not None and d > bound:
            break
        done.add(u)
        for hi in hosp_at.get(u, ()):
            h = hospitals[hi]
            if suitable(h, prof):
                found.append(tie_key(d, h))
                if bound is None and len(found) >= k:
                    bound = d
        for v, w in adj[u]:
            nd = d + w
            if nd < dist.get(v, INF):
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    found.sort()
    return found[:k], len(done)


def full_search(adj, src):
    dist = {src: 0.0}
    pq = [(0.0, src)]
    done = set()
    while pq:
        d, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u)
        for v, w in adj[u]:
            nd = d + w
            if nd < dist.get(v, INF):
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist


def catchment_map(adj_rev, n, hospitals, prof):
    """One multi-source search with lexicographic labels (Proposition 16).

    Returns label[v] = (T*, -b, id) of the nearest suitable hospital of v and the
    set of road segments in the shortest-path forest.
    """
    label = [None] * n
    parent = [None] * n
    pq = []
    for h in hospitals:
        if suitable(h, prof):
            heapq.heappush(pq, (tie_key(0.0, h), h["node"], None))
    while pq:
        key, u, par = heapq.heappop(pq)
        if label[u] is not None:
            continue
        label[u] = key
        parent[u] = par
        for v, w in adj_rev[u]:
            if label[v] is None:
                heapq.heappush(pq, ((key[0] + w, key[1], key[2]), v, u))
    forest = set()
    for v in range(n):
        if parent[v] is not None:
            a, b = (v, parent[v]) if v < parent[v] else (parent[v], v)
            forest.add((a, b))
    return label, forest


# ---------------------------------------------------------------- inequality
def weighted_gini(A, P):
    A = np.asarray(A, float); P = np.asarray(P, float)
    W = P.sum(); mu = (P * A).sum() / W
    if mu == 0:
        return 0.0
    return float((np.outer(P, P) * np.abs(A[:, None] - A[None, :])).sum() / (2 * W * W * mu))


def theil(A, P):
    A = np.asarray(A, float); P = np.asarray(P, float)
    W = P.sum(); mu = (P * A).sum() / W
    t = 0.0
    for a, p in zip(A, P):
        if a > 0:
            t += (p / W) * (a / mu) * math.log(a / mu)
    return t


def theil_split(A, P, groups):
    A = np.asarray(A, float); P = np.asarray(P, float)
    W = P.sum(); mu = (P * A).sum() / W
    within = between = 0.0
    for g in sorted(set(groups)):
        idx = [i for i, x in enumerate(groups) if x == g]
        Wg = P[idx].sum(); mug = (P[idx] * A[idx]).sum() / Wg
        if mug == 0:
            continue
        sg = Wg * mug / (W * mu)
        within += sg * theil(A[idx], P[idx])
        between += sg * math.log(mug / mu)
    return within, between


def lorenz_value(A, P, x):
    order = np.argsort(A, kind="stable")
    A = np.asarray(A, float)[order]; P = np.asarray(P, float)[order]
    cw = np.concatenate([[0], np.cumsum(P) / P.sum()])
    tot = (A * P).sum()
    ca = np.concatenate([[0], np.cumsum(A * P) / tot]) if tot > 0 else np.zeros(len(cw))
    return float(np.interp(x, cw, ca))


def palma(A, P):
    bottom = lorenz_value(A, P, 0.4)
    top = 1 - lorenz_value(A, P, 0.9)
    return INF if bottom == 0 else top / bottom


def two_step_fca(T, P, supply, theta):
    """Two-step floating catchment area (Luo & Wang, 2003) on anchors x hospitals."""
    na, nh = T.shape
    R = np.zeros(nh)
    for j in range(nh):
        pop = sum(P[i] for i in range(na) if T[i, j] <= theta)
        R[j] = supply[j] / pop if pop > 0 else 0.0
    A = np.array([sum(R[j] for j in range(nh) if T[i, j] <= theta) for i in range(na)])
    return R, A


# ---------------------------------------------------------------- surge assignment
def assign_optimal(times, suit, beds, emergency):
    """Minimum-cost assignment of patients to bed slots (Proposition 18).

    times[i][j]: travel time of patient i to hospital j (inf if unreachable)
    suit[i][j]: suitability; beds[j]: free beds; emergency[i]: bool.
    Unplaced patients cost U (1e8 if emergency, 1e6 otherwise), so the solver
    places as many emergency patients as possible, then as many others, then
    minimises total travel time.
    """
    m = len(times)
    slots = [j for j, b in enumerate(beds) for _ in range(b)]
    BIG = 1e12
    C = np.full((m, len(slots) + m), BIG)
    for i in range(m):
        for s, j in enumerate(slots):
            if suit[i][j] and times[i][j] < INF:
                C[i, s] = times[i][j]
        C[i, len(slots) + i] = 1e8 if emergency[i] else 1e6
    r, c = linear_sum_assignment(C)
    out = [None] * m
    for i, col in zip(r, c):
        out[i] = slots[col] if col < len(slots) else None
    return out


def assign_independent(times, suit):
    out = []
    for i in range(len(times)):
        best = None
        for j in range(len(times[i])):
            if suit[i][j] and times[i][j] < INF and (best is None or times[i][j] < times[i][best]):
                best = j
        out.append(best)
    return out


def assign_sequential(times, suit, beds, order):
    left = list(beds)
    out = [None] * len(times)
    for i in order:
        best = None
        for j in range(len(times[i])):
            if left[j] > 0 and suit[i][j] and times[i][j] < INF and (best is None or times[i][j] < times[i][best]):
                best = j
        if best is not None:
            left[best] -= 1
            out[i] = best
    return out


def total_time(times, out):
    return sum(times[i][j] for i, j in enumerate(out) if j is not None)


# ---------------------------------------------------------------- timetable router (patient mode)
def random_timetable(rng):
    n_stops = rng.randint(12, 20)
    pts = [(rng.random() * 6.0, rng.random() * 6.0) for _ in range(n_stops)]
    conns = []   # (dep_stop, arr_stop, t_dep, t_arr, trip)
    trip = 0
    for _ in range(rng.randint(4, 6)):
        seq = rng.sample(range(n_stops), rng.randint(4, 7))
        hops = [rng.uniform(2.0, 8.0) for _ in seq[1:]]
        headway = rng.choice([10, 15, 20, 30])
        for direction in (seq, seq[::-1]):
            hp = hops if direction is seq else hops[::-1]
            start = 360 + rng.uniform(0, headway)
            while start < 540:
                t = start
                for a, b, h in zip(direction, direction[1:], hp):
                    conns.append((a, b, t, t + h, trip))
                    t += h
                trip += 1
                start += headway
    hosp_pts = []
    for _ in range(rng.randint(3, 6)):   # hospitals stand near a road that a route uses
        sx, sy = pts[rng.randrange(n_stops)]
        ang, rad = rng.uniform(0, 2 * math.pi), rng.uniform(0.1, 0.8)
        hosp_pts.append((sx + rad * math.cos(ang), sy + rad * math.sin(ang)))
    return pts, conns, hosp_pts


def walk_min(p, q, kmh):
    return math.dist(p, q) * 1.2 / kmh * 60.0


class TimetableRouter:
    """Label-setting search on the time-expanded graph of Definition 5, with hospital sinks."""

    def __init__(self, pts, conns, hosp_pts, theta_ch=4.0):
        self.pts, self.hosp_pts, self.theta_ch = pts, hosp_pts, theta_ch
        self.conns = conns
        self.next_in_trip = {}
        by_trip = {}
        for ci, c in enumerate(conns):
            by_trip.setdefault(c[4], []).append(ci)
        for lst in by_trip.values():
            lst.sort(key=lambda ci: conns[ci][2])
            for a, b in zip(lst, lst[1:]):
                self.next_in_trip[a] = b
        self.dep_at = {s: [] for s in range(len(pts))}
        for ci, c in enumerate(conns):
            self.dep_at[c[0]].append(ci)
        for s in self.dep_at:
            self.dep_at[s].sort(key=lambda ci: conns[ci][2])
        self.dep_times = {s: [conns[ci][2] for ci in self.dep_at[s]] for s in self.dep_at}

    def _wait_node(self, s, t):
        i = bisect.bisect_left(self.dep_times[s], t)
        if i < len(self.dep_at[s]):
            return ("W", s, i), self.dep_times[s][i]
        return None, None

    def search(self, origin, t0, kmh, cap, hospitals, prof, k=1, early=True):
        pq = []
        push = lambda lab, node: heapq.heappush(pq, (lab, node))

        def walk_from(s, t):
            for s2 in range(len(self.pts)):
                if s2 == s:
                    continue
                w = walk_min(self.pts[s], self.pts[s2], kmh)
                if w <= cap:
                    node, lab = self._wait_node(s2, t + w)
                    if node:
                        push(lab, node)
            for hi, hp in enumerate(self.hosp_pts):
                w = walk_min(self.pts[s], hp, kmh)
                if w <= cap:
                    push(t + w, ("Z", hi))

        node, lab = self._wait_node(origin, t0)
        if node:
            push(lab, node)
        walk_from(origin, t0)
        done = set()
        found = []
        bound = None
        while pq:
            lab, node = heapq.heappop(pq)
            if node in done:
                continue
            if early and bound is not None and lab > bound:
                break
            done.add(node)
            kind = node[0]
            if kind == "Z":
                h = hospitals[node[1]]
                if suitable(h, prof):
                    found.append(tie_key(lab - t0, h))
                    if bound is None and len(found) >= k:
                        bound = lab
            elif kind == "W":
                _, s, i = node
                ci = self.dep_at[s][i]
                push(self.conns[ci][2], ("D", ci))
                if i + 1 < len(self.dep_at[s]):
                    push(self.dep_times[s][i + 1], ("W", s, i + 1))
            elif kind == "D":
                ci = node[1]
                push(self.conns[ci][3], ("A", ci))
            else:   # arrival event
                ci = node[1]
                s, t = self.conns[ci][1], self.conns[ci][3]
                nxt = self.next_in_trip.get(ci)
                if nxt is not None:
                    push(self.conns[nxt][2], ("D", nxt))
                wnode, wlab = self._wait_node(s, t + self.theta_ch)
                if wnode:
                    push(wlab, wnode)
                walk_from(s, t)
        found.sort()
        return found[:k] if early else found


# ================================================================ experiments
def exp_ambulance(rng):
    """Early stopping with backups, need monotonicity (Tables 25 and 26)."""
    r = {"graphs": 0, "queries": 0, "reachable": 0, "agree_k1": 0, "agree_k3": 0,
         "need_set_checks": 0, "need_time_checks": 0, "need_violations": 0,
         "diversion": []}
    for _ in range(200):
        n = rng.randint(120, 260)
        pts, segs = road_graph(rng, n)
        adj = adjacency(n, segs)
        hs = random_hospitals(rng, n, rng.randint(6, 15))
        hosp_at = {}
        for i, h in enumerate(hs):
            hosp_at.setdefault(h["node"], []).append(i)
        D = floyd_warshall(n, adj)
        r["graphs"] += 1
        for _ in range(20):
            o = rng.randrange(n)
            prof = random_profile(rng)
            ref = sorted(tie_key(float(D[o, h["node"]]), h) for h in hs
                         if suitable(h, prof) and D[o, h["node"]] < INF)
            got1, _ = k_nearest_suitable(adj, o, hosp_at, hs, prof, k=1)
            got3, _ = k_nearest_suitable(adj, o, hosp_at, hs, prof, k=3)
            r["queries"] += 1
            if ref:
                r["reachable"] += 1
            same = lambda a, b: len(a) == len(b) and all(x[2] == y[2] and abs(x[0] - y[0]) < 1e-9 for x, y in zip(a, b))
            r["agree_k1"] += same(got1, ref[:1])
            r["agree_k3"] += same(got3, ref[:3])
            if len(ref) >= 2:
                r["diversion"].append(ref[1][0] - ref[0][0])
            # need monotonicity: every superset of the need set
            rest = [s for s in SERVICES if s not in prof["needs"]]
            for extra in rest:
                bigger = dict(prof, needs=prof["needs"] | {extra})
                H1 = {h["id"] for h in hs if suitable(h, prof)}
                H2 = {h["id"] for h in hs if suitable(h, bigger)}
                r["need_set_checks"] += 1
                if not H2 <= H1:
                    r["need_violations"] += 1
                t1 = min([D[o, h["node"]] for h in hs if h["id"] in H1], default=INF)
                t2 = min([D[o, h["node"]] for h in hs if h["id"] in H2], default=INF)
                r["need_time_checks"] += 1
                if t1 > t2 + 1e-12:
                    r["need_violations"] += 1
    dv = r.pop("diversion")
    r["diversion_cases"] = len(dv)
    r["diversion_median"] = float(np.median(dv))
    r["diversion_mean"] = float(np.mean(dv))
    return r


def exp_catchment(rng):
    """Catchment map from one search versus one search per vertex (Table 27)."""
    r = {"graphs": 0, "vertices": 0, "agree": 0, "segments_tested": 0,
         "segments_in_forest": 0, "positive_delay": 0, "positive_outside_forest": 0,
         "zero_inside_forest": 0}
    for _ in range(60):
        n = rng.randint(120, 260)
        pts, segs = road_graph(rng, n)
        adj = adjacency(n, segs)
        hs = random_hospitals(rng, n, rng.randint(6, 15))
        hosp_at = {}
        for i, h in enumerate(hs):
            hosp_at.setdefault(h["node"], []).append(i)
        prof = random_profile(rng, need_max=1)
        while not any(suitable(h, prof) for h in hs):
            prof = random_profile(rng, need_max=1)
        label, forest = catchment_map(adj, n, hs, prof)
        r["graphs"] += 1
        for v in range(n):
            got, _ = k_nearest_suitable(adj, v, hosp_at, hs, prof, k=1)
            r["vertices"] += 1
            if (label[v] is None and not got) or (label[v] is not None and got and label[v][2] == got[0][2] and abs(label[v][0] - got[0][0]) < 1e-9):
                r["agree"] += 1
        # critical segments: brute force over every open segment
        for seg, (w, is_open) in segs.items():
            if not is_open:
                continue
            r["segments_tested"] += 1
            in_f = seg in forest
            r["segments_in_forest"] += in_f
            lab2, _ = catchment_map(adjacency(n, segs, skip=seg), n, hs, prof)
            changed = any((a is None) != (b is None) or (a is not None and (a[0] > b[0] + 1e-9 or a[2] != b[2]))
                          for a, b in zip(lab2, label))
            r["positive_delay"] += changed
            if changed and not in_f:
                r["positive_outside_forest"] += 1
            if in_f and not changed:
                r["zero_inside_forest"] += 1
    return r


def exp_catchment_timing(rng):
    rows = []
    for n in (1000, 4000, 16000):
        pts, segs = road_graph(rng, n)
        adj = adjacency(n, segs)
        hs = random_hospitals(rng, n, max(1, n // 150))
        for h in hs:   # keep the timing about distance, not about filters
            h.update(level=3, services=LEVEL_SERVICES[3], er=True, q=0, status="AVAILABLE", b=5)
        hosp_at = {}
        for i, h in enumerate(hs):
            hosp_at.setdefault(h["node"], []).append(i)
        prof = {"kappa": 3, "rho": 3, "needs": frozenset()}
        t = time.perf_counter()
        for _ in range(5):
            catchment_map(adj, n, hs, prof)
        multi = (time.perf_counter() - t) / 5 * 1000
        sample = rng.sample(range(n), 300)
        t = time.perf_counter()
        for v in sample:
            k_nearest_suitable(adj, v, hosp_at, hs, prof, k=1)
        per = (time.perf_counter() - t) / len(sample) * 1000
        rows.append({"vertices": n, "segments": len(segs), "hospitals": len(hs),
                     "one_search_ms": round(multi, 2), "per_origin_ms": round(per, 3),
                     "all_origins_ms": round(per * n, 0), "speedup": round(per * n / multi, 1)})
    return rows


def exp_2sfca(rng):
    """Conservation of beds under 2SFCA (Proposition 17)."""
    worst = 0.0
    for _ in range(500):
        na, nh = rng.randint(5, 40), rng.randint(2, 10)
        T = np.array([[rng.uniform(0, 90) for _ in range(nh)] for _ in range(na)])
        P = np.array([rng.randint(100, 9000) for _ in range(na)], float)
        S = np.array([rng.randint(0, 60) for _ in range(nh)], float)
        R, A = two_step_fca(T, P, S, 30.0)
        reach = [j for j in range(nh) if (T[:, j] <= 30.0).any()]
        worst = max(worst, abs(float((P * A).sum()) - float(S[reach].sum())))
    return {"instances": 500, "largest_residual": worst}


def exp_surge(rng):
    """Many patients, few beds (Table 30)."""
    r = {"instances": 0, "patients": 0, "turned_away_independent": 0,
         "placed_sequential": 0, "placed_optimal": 0, "opt_more_placed": 0,
         "equal_placed": 0, "time_saved_when_equal": [], "fits_cases": 0, "fits_equal": 0,
         "emerg_unplaced_seq": 0, "emerg_unplaced_opt": 0}
    for _ in range(300):
        n = rng.randint(120, 260)
        pts, segs = road_graph(rng, n)
        adj = adjacency(n, segs)
        hs = random_hospitals(rng, n, rng.randint(6, 12))
        for h in hs:
            h["status"] = "AVAILABLE"
            h["b"] = rng.randint(0, 6)
            if h["b"] == 0:
                h["status"] = "FULL"
        D = floyd_warshall(n, adj)
        m = rng.randint(15, 45)
        pats = [(rng.randrange(n), random_profile(rng, need_max=1)) for _ in range(m)]
        times = [[float(D[o, h["node"]]) for h in hs] for o, _ in pats]
        # suitability without the FULL test; capacity is handled by the beds
        suit = [[suitable(dict(h, status="AVAILABLE"), p) for h in hs] for _, p in pats]
        beds = [h["b"] for h in hs]
        emerg = [p["kappa"] in KE for _, p in pats]
        ind = assign_independent(times, suit)
        load = {}
        for j in ind:
            if j is not None:
                load[j] = load.get(j, 0) + 1
        turned = sum(max(0, c - beds[j]) for j, c in load.items())
        order = sorted(range(m), key=lambda i: (not emerg[i], rng.random()))
        seq = assign_sequential(times, suit, beds, order)
        opt = assign_optimal(times, suit, beds, emerg)
        ps = sum(j is not None for j in seq)
        po = sum(j is not None for j in opt)
        r["instances"] += 1
        r["patients"] += m
        r["turned_away_independent"] += turned
        r["placed_sequential"] += ps
        r["placed_optimal"] += po
        r["emerg_unplaced_seq"] += sum(1 for i in range(m) if emerg[i] and seq[i] is None)
        r["emerg_unplaced_opt"] += sum(1 for i in range(m) if emerg[i] and opt[i] is None)
        es = sum(1 for i in range(m) if emerg[i] and seq[i] is not None)
        eo = sum(1 for i in range(m) if emerg[i] and opt[i] is not None)
        if po > ps:
            r["opt_more_placed"] += 1
        elif po == ps and es == eo:
            # same number of emergency and other patients placed: compare travel time
            r["equal_placed"] += 1
            r["time_saved_when_equal"].append(total_time(times, seq) - total_time(times, opt))
        assert po >= ps
        if turned == 0:
            r["fits_cases"] += 1
            if abs(total_time(times, ind) - total_time(times, opt)) < 1e-6 and all((a is None) == (b is None) for a, b in zip(ind, opt)):
                r["fits_equal"] += 1
    ts = r.pop("time_saved_when_equal")
    r["min_time_saved_when_equal"] = float(min(ts))
    r["mean_time_saved_when_equal"] = float(np.mean(ts))
    r["share_strictly_better_when_equal"] = float(np.mean([t > 1e-6 for t in ts]))
    return r


def exp_cover(rng):
    """Greedy choice of Malasakit Center sites versus the true optimum (Table 31)."""
    ratios = []
    for _ in range(500):
        na, nc = 30, 12
        A = [(rng.random() * 20, rng.random() * 20) for _ in range(na)]
        P = [rng.randint(200, 6000) for _ in range(na)]
        C = [(rng.random() * 20, rng.random() * 20) for _ in range(nc)]
        E = [(rng.random() * 20, rng.random() * 20) for _ in range(2)]
        speed = rng.uniform(18, 30)
        T = lambda a, c: math.dist(a, c) * 1.3 / speed * 60
        covered0 = {i for i in range(na) for e in E if T(A[i], e) <= 30}
        cover = [{i for i in range(na) if T(A[i], C[j]) <= 30} for j in range(nc)]
        f = lambda S: sum(P[i] for i in (covered0.union(*[cover[j] for j in S]) if S else covered0) if i not in covered0)
        k = rng.randint(1, 4)
        S = []
        for _ in range(k):
            best = max((j for j in range(nc) if j not in S), key=lambda j: (f(S + [j]), -j))
            S.append(best)
        opt = max(f(list(c)) for c in itertools.combinations(range(nc), k))
        if opt > 0:
            ratios.append(f(S) / opt)
    return {"instances": len(ratios), "min_ratio": min(ratios), "mean_ratio": float(np.mean(ratios)),
            "share_optimal": float(np.mean([x > 1 - 1e-12 for x in ratios])), "bound": 1 - 1 / math.e}


def exp_mobility(rng):
    """Slow walkers in patient mode (Proposition 14, Table 28)."""
    r = {"timetables": 0, "queries": 0, "violations": 0, "both_reach": 0, "changed_hospital": 0,
         "extra": [], "lost_all": 0, "early_agree": 0, "early_checks": 0}
    for _ in range(120):
        pts, conns, hosp_pts = random_timetable(rng)
        hs = []
        for i in range(len(hosp_pts)):
            level = rng.choice([1, 2, 3])
            hs.append({"id": i, "level": level, "services": LEVEL_SERVICES[level], "er": True,
                       "q": rng.choice([0, 1, 2, 3]), "status": rng.choice(["AVAILABLE", "AVAILABLE", "FULL", "UNKNOWN"]),
                       "b": rng.randint(1, 10)})
        router = TimetableRouter(pts, conns, hosp_pts)
        r["timetables"] += 1
        for _ in range(10):
            o = rng.randrange(len(pts))
            t0 = rng.uniform(360, 450)
            prof = random_profile(rng, need_max=1)
            std = router.search(o, t0, 4.5, 15.0, hs, prof)
            slow = router.search(o, t0, 3.0, 10.0, hs, prof)
            ref_all = router.search(o, t0, 4.5, 15.0, hs, prof, early=False)
            r["early_checks"] += 1
            r["early_agree"] += (std == ref_all[:1]) or (std and ref_all and std[0][2] == ref_all[0][2] and abs(std[0][0] - ref_all[0][0]) < 1e-9)
            r["queries"] += 1
            ts = std[0][0] if std else INF
            tl = slow[0][0] if slow else INF
            if tl < ts - 1e-9:
                r["violations"] += 1
            if std and slow:
                r["both_reach"] += 1
                r["extra"].append(tl - ts)
                if std[0][2] != slow[0][2]:
                    r["changed_hospital"] += 1
            elif std and not slow:
                r["lost_all"] += 1
    ex = r.pop("extra")
    r["mean_extra"] = float(np.mean(ex))
    r["max_extra"] = float(np.max(ex))
    r["share_extra_positive"] = float(np.mean([x > 1e-9 for x in ex]))
    return r


# ---------------------------------------------------------------- instance S1
def s1():
    anchors = ["A1", "A2", "A3", "A4", "A5", "A6"]
    P = np.array([4200, 3100, 1850, 1400, 980, 2600], float)
    muni = ["M1", "M1", "M1", "M2", "M2", "M2"]
    sites = ["S4", "S7", "S3"]
    T = np.array([[29.2, 49.0, 24.6], [27.3, 61.0, 21.3], [18.6, 51.4, 7.0],
                  [43.6, 76.6, 37.5], [32.6, 65.8, 26.0], [37.2, 13.0, 48.1]])
    auth = np.array([120, 40, 25], float)
    free = np.array([8, 9, 0], float)
    hs = [
        {"id": 4, "name": "S4", "level": 3, "services": LEVEL_SERVICES[3], "er": True, "q": 0, "status": "AVAILABLE", "b": 8},
        {"id": 7, "name": "S7", "level": 2, "services": LEVEL_SERVICES[2], "er": True, "q": 2, "status": "AVAILABLE", "b": 9},
        {"id": 3, "name": "S3", "level": 1, "services": LEVEL_SERVICES[1], "er": True, "q": 1, "status": "FULL", "b": 0},
    ]
    out = {}
    # consistency with Table 17
    A30 = np.array([sum(auth[j] for j in range(3) if T[i, j] <= 30) for i in range(6)])
    w, b = theil_split(A30, P, muni)
    out["check_table17"] = {"A30": A30.tolist(), "gini": round(weighted_gini(A30, P), 4),
                            "theil": round(theil(A30, P), 4), "within": round(w, 4), "between": round(b, 4),
                            "palma": round(palma(A30, P), 3)}
    # 2SFCA
    rows = {}
    for name, supply in (("authorized", auth), ("free", free)):
        R, A = two_step_fca(T, P, supply, 30.0)
        wi, be = theil_split(A, P, muni)
        rows[name] = {"R_per_10000": [round(x * 1e4, 2) for x in R],
                      "A_per_10000": [round(x * 1e4, 2) for x in A],
                      "weighted_mean_per_10000": round(float((P * A).sum() / P.sum()) * 1e4, 3),
                      "conservation_lhs": round(float((P * A).sum()), 6),
                      "gini": round(weighted_gini(A, P), 4), "theil": round(theil(A, P), 4),
                      "within_share": round(wi / (wi + be), 3) if wi + be > 0 else None,
                      "zero_share": round(float(P[A == 0].sum() / P.sum()), 3)}
    out["two_step_fca"] = rows
    # needs, with backups (kappa = 3)
    needs_rows = []
    for need_name, needs in (("none", frozenset()), ("normal delivery (MAT)", frozenset({"MAT"})),
                             ("high-risk pregnancy (HRP)", frozenset({"HRP"})),
                             ("dialysis (DIA)", frozenset({"DIA"}))):
        for rho in (3, 0):
            prof = {"kappa": 3, "rho": rho, "needs": needs}
            row = {"need": need_name, "rho": rho, "by_anchor": []}
            for i in range(6):
                ranked = sorted(tie_key(T[i, j], hs[j]) for j in range(3) if suitable(hs[j], prof))
                names = {h["id"]: h["name"] for h in hs}
                row["by_anchor"].append([(names[k[2]], k[0]) for k in ranked[:2]])
            needs_rows.append(row)
    out["needs"] = needs_rows
    # need gap for dialysis, rho = 3
    base = [min(T[i, j] for j in range(3) if suitable(hs[j], {"kappa": 3, "rho": 3, "needs": frozenset()})) for i in range(6)]
    dia = [min(T[i, j] for j in range(3) if suitable(hs[j], {"kappa": 3, "rho": 3, "needs": frozenset({"DIA"})})) for i in range(6)]
    gap = np.array(dia) - np.array(base)
    out["need_gap_dialysis"] = {"by_anchor": [round(x, 1) for x in gap], "weighted_mean": round(float((P * gap).sum() / P.sum()), 2)}
    # surge scenario: kappa = 2, patients per anchor
    counts = [4, 3, 2, 2, 1, 3]
    prof = {"kappa": 2, "rho": 0, "needs": frozenset()}
    pats = [i for i in range(6) for _ in range(counts[i])]
    times = [[T[i, j] for j in range(3)] for i in pats]
    suit = [[suitable(dict(hs[j], status="AVAILABLE"), prof) for j in range(3)] for _ in pats]
    beds = [8, 9, 0]
    ind = assign_independent(times, suit)
    opt = assign_optimal(times, suit, beds, [True] * len(pats))
    load_ind = [sum(1 for j in ind if j == k) for k in range(3)]
    load_opt = [sum(1 for j in opt if j == k) for k in range(3)]
    per_anchor = {}
    for idx, i in enumerate(pats):
        per_anchor.setdefault(anchors[i], []).append(sites[opt[idx]] if opt[idx] is not None else "none")
    out["surge"] = {"patients_per_anchor": counts, "independent_load": load_ind, "optimal_load": load_opt,
                    "turned_away_independent": sum(max(0, load_ind[k] - beds[k]) for k in range(3)),
                    "total_time_independent_if_unlimited": round(total_time(times, ind), 1),
                    "total_time_optimal": round(total_time(times, opt), 1),
                    "assignment": per_anchor}
    return out


def main():
    rng = random.Random(SEED)
    results = {"seed": SEED}
    t = time.perf_counter()
    results["S1"] = s1()
    results["ambulance"] = exp_ambulance(rng)
    results["catchment"] = exp_catchment(rng)
    results["catchment_timing"] = exp_catchment_timing(rng)
    results["two_step_fca_random"] = exp_2sfca(rng)
    results["surge"] = exp_surge(rng)
    results["cover"] = exp_cover(rng)
    results["mobility"] = exp_mobility(rng)
    results["runtime_s"] = round(time.perf_counter() - t, 1)
    print(json.dumps(results, indent=1, default=float))


if __name__ == "__main__":
    main()
