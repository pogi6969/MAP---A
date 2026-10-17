"""Safe Shelter, Open Schools: core model.

Shelter assignment as a lexicographic minimum-cost flow, classroom packing,
evacuation over time on a time-expanded network, and coverage-based siting
of new evacuation centers (Ligtas Pinoy Centers).

Every algorithm here is the one described in Section 2 of the paper; the
independent reference implementations used to check it live in
verify_evacuation.py.
"""

import heapq
import itertools
import math

import networkx as nx

SPHERE_M2 = 3.5                          # covered living space per person (Sphere)
CLASSROOM_M2 = 63.0                      # 7 m x 9 m standard classroom
Q_CLASSROOM = int(CLASSROOM_M2 // SPHERE_M2)   # evacuees per classroom = 18

TIER_EC, TIER_OPEN, TIER_ROOM = 0, 1, 2  # non-school, school open space, classroom
TIER_NAMES = {TIER_EC: "non-school", TIER_OPEN: "school open space",
              TIER_ROOM: "classroom"}


def capacity_from_area(area_m2):
    """Equation (5): persons a covered floor area can hold."""
    return int(area_m2 // SPHERE_M2)


# ---------------------------------------------------------------------------
# Instance
# ---------------------------------------------------------------------------

class Instance:
    """Road graph, origins, and shelters.

    arcs: list of (tail, head, tau, cap, tag); tau in time steps (>= 1),
          cap in persons per time step, tag a label used for closures.
    origins: list of dicts with keys id, node, pop, vul, zones (set of
          hazard names the origin lies in).
    shelters: list of dicts with keys id, node, kind ('ec' or 'school'),
          cap_ec, cap_open, rooms, q, accessible (bool), zones (set),
          learners_per_room.
    """

    def __init__(self, nodes, arcs, origins, shelters, theta_max=10 ** 9):
        self.nodes = list(nodes)
        self.arcs = list(arcs)
        self.origins = list(origins)
        self.shelters = list(shelters)
        self.theta_max = theta_max

    def open_arcs(self, closed_tags=()):
        closed = set(closed_tags)
        return [a for a in self.arcs if a[4] not in closed]

    def adjacency(self, closed_tags=()):
        adj = {v: [] for v in self.nodes}
        for (u, v, tau, cap, tag) in self.open_arcs(closed_tags):
            adj[u].append((v, tau))
        return adj


class Scenario:
    """A hazard scenario: which hazard zones are active and which arcs close."""

    def __init__(self, name, zones, closed_tags=()):
        self.name = name
        self.zones = set(zones)
        self.closed_tags = tuple(closed_tags)

    def demand(self, o):
        return o["pop"] if o["zones"] & self.zones else 0

    def vulnerable(self, o):
        return o["vul"] if o["zones"] & self.zones else 0

    def shelter_safe(self, s):
        return not (s["zones"] & self.zones)


# ---------------------------------------------------------------------------
# Shortest travel times
# ---------------------------------------------------------------------------

def dijkstra(adj, src):
    dist = {src: 0}
    heap = [(0, src)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist.get(u, math.inf):
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return dist


def travel_times(inst, scen):
    """T[a][s]: shortest time from origin a to shelter s on the open graph."""
    adj = inst.adjacency(scen.closed_tags)
    T = {}
    for a, o in enumerate(inst.origins):
        dist = dijkstra(adj, o["node"])
        T[a] = {s: dist.get(sh["node"], math.inf)
                for s, sh in enumerate(inst.shelters)}
    return T


# ---------------------------------------------------------------------------
# Shelter slots and suitability
# ---------------------------------------------------------------------------

def slots(inst, scen, extra_caps=None):
    """List of (shelter index, tier, capacity, accessible) for safe shelters."""
    out = []
    for s, sh in enumerate(inst.shelters):
        if not scen.shelter_safe(sh):
            continue
        add = (extra_caps or {}).get(s, 0)
        if sh["cap_ec"] + add > 0:
            out.append((s, TIER_EC, sh["cap_ec"] + add, sh["accessible"]))
        if sh["cap_open"] > 0:
            out.append((s, TIER_OPEN, sh["cap_open"], sh["accessible"]))
        if sh["rooms"] > 0:
            out.append((s, TIER_ROOM, sh["rooms"] * sh["q"], sh["accessible"]))
    return out


def suitable(inst, scen, T, a, slot, vulnerable):
    """Definition 10: can a person from origin a use this slot?"""
    s, tier, cap, acc = slot
    if T[a][s] > inst.theta_max:
        return False
    if vulnerable and not acc:
        return False
    return True


# ---------------------------------------------------------------------------
# Lexicographic shelter assignment (Definition 11, Algorithm 1)
# ---------------------------------------------------------------------------

def _flow_network(inst, scen, T, sl, include_vul=True, include_non=True):
    G = nx.DiGraph()
    G.add_node("SRC")
    G.add_node("SNK")
    for a, o in enumerate(inst.origins):
        d, v = scen.demand(o), scen.vulnerable(o)
        if include_vul and v > 0:
            G.add_edge("SRC", ("o", a, "V"), capacity=v)
        if include_non and d - v > 0:
            G.add_edge("SRC", ("o", a, "N"), capacity=d - v)
    for k, slot in enumerate(sl):
        G.add_edge(("slot", k), "SNK", capacity=slot[2])
        for a, o in enumerate(inst.origins):
            if include_vul and scen.vulnerable(o) > 0 and suitable(inst, scen, T, a, slot, True):
                G.add_edge(("o", a, "V"), ("slot", k))
            if include_non and scen.demand(o) - scen.vulnerable(o) > 0 and \
                    suitable(inst, scen, T, a, slot, False):
                G.add_edge(("o", a, "N"), ("slot", k))
    return G


def _max_flow(G):
    if G.number_of_edges() == 0:
        return 0
    return nx.maximum_flow_value(G, "SRC", "SNK")


def penalties(inst, scen, T):
    """Penalty weights of Proposition 3 (exact integers)."""
    D = sum(scen.demand(o) for o in inst.origins)
    finite = [T[a][s] for a in T for s in T[a] if T[a][s] <= inst.theta_max]
    tmax = max(finite) if finite else 0
    m_open = D * tmax + 1
    m_room = D * (m_open + tmax) + 1
    return m_open, m_room


def lex_plan(inst, scen, policy="lex", extra_caps=None):
    """Shelter plan.

    policy 'lex'   : vulnerable placed, then total placed (both maximized),
                     then persons in classrooms, persons in school open
                     spaces, and person-minutes (all minimized).
    policy 'blind' : same first two levels, then person-minutes only.
    """
    T = travel_times(inst, scen)
    sl = slots(inst, scen, extra_caps)
    fv = _max_flow(_flow_network(inst, scen, T, sl, include_non=False))
    ftot = _max_flow(_flow_network(inst, scen, T, sl))
    m_open, m_room = penalties(inst, scen, T)
    G = nx.DiGraph()
    G.add_node("SV", demand=-fv)
    G.add_node("SN", demand=-(ftot - fv))
    G.add_node("SNK", demand=ftot)
    for a, o in enumerate(inst.origins):
        d, v = scen.demand(o), scen.vulnerable(o)
        if v > 0:
            G.add_edge("SV", ("o", a, "V"), capacity=v, weight=0)
        if d - v > 0:
            G.add_edge("SN", ("o", a, "N"), capacity=d - v, weight=0)
    for k, slot in enumerate(sl):
        s, tier, cap, acc = slot
        G.add_edge(("slot", k), "SNK", capacity=cap, weight=0)
        pen = 0
        if policy == "lex":
            pen = {TIER_EC: 0, TIER_OPEN: m_open, TIER_ROOM: m_room}[tier]
        for a, o in enumerate(inst.origins):
            for cls, vul in (("V", True), ("N", False)):
                if not G.has_node(("o", a, cls)):
                    continue
                if suitable(inst, scen, T, a, slot, vul):
                    G.add_edge(("o", a, cls), ("slot", k), weight=int(T[a][s]) + pen)
    if ftot == 0:
        flow = {}
    else:
        _, flow = nx.network_simplex(G)
    return summarize_plan(inst, scen, T, sl, flow, fv, ftot)


def summarize_plan(inst, scen, T, sl, flow, fv, ftot):
    x = {}                      # (a, k, cls) -> persons
    for a, o in enumerate(inst.origins):
        for cls in ("V", "N"):
            node = ("o", a, cls)
            for k in range(len(sl)):
                f = flow.get(node, {}).get(("slot", k), 0)
                if f:
                    x[(a, k, cls)] = f
    by_tier = {TIER_EC: 0, TIER_OPEN: 0, TIER_ROOM: 0}
    room_persons = {}
    person_min = 0
    load = {}
    for (a, k, cls), f in x.items():
        s, tier, cap, acc = sl[k]
        by_tier[tier] += f
        person_min += f * T[a][s]
        load[s] = load.get(s, 0) + f
        if tier == TIER_ROOM:
            room_persons[s] = room_persons.get(s, 0) + f
    rooms_closed = {s: math.ceil(y / inst.shelters[s]["q"]) for s, y in room_persons.items() if y > 0}
    learners = sum(rooms_closed[s] * inst.shelters[s]["learners_per_room"] for s in rooms_closed)
    D = sum(scen.demand(o) for o in inst.origins)
    V = sum(scen.vulnerable(o) for o in inst.origins)
    times = [T[a][sl[k][0]] for (a, k, cls), f in x.items() for _ in range(1)]
    max_time = max(times) if times else 0
    return {
        "x": x, "slots": sl, "T": T, "demand": D, "vulnerable": V,
        "vul_placed": fv, "placed": ftot, "unplaced": D - ftot,
        "persons_ec": by_tier[TIER_EC], "persons_open": by_tier[TIER_OPEN],
        "persons_room": by_tier[TIER_ROOM], "room_persons": room_persons,
        "rooms_closed": rooms_closed, "rooms_closed_total": sum(rooms_closed.values()),
        "learners_displaced": learners, "person_minutes": person_min,
        "mean_time": person_min / ftot if ftot else 0.0, "max_time": max_time,
        "load": load,
    }


def nearest_plan(inst, scen):
    """Baseline: every origin goes to its nearest safe, reachable shelter site.

    Shelters that share a road node form one site, so a family that finds one
    of them full may use another at the same place.
    """
    T = travel_times(inst, scen)
    site_cap, site_time = {}, {}
    for s, sh in enumerate(inst.shelters):
        if scen.shelter_safe(sh):
            cap = sh["cap_ec"] + sh["cap_open"] + sh["rooms"] * sh["q"]
            site_cap[sh["node"]] = site_cap.get(sh["node"], 0) + cap
    load = {}
    person_min = 0
    for a, o in enumerate(inst.origins):
        d = scen.demand(o)
        if d == 0:
            continue
        cands = sorted({(T[a][s], sh["node"]) for s, sh in enumerate(inst.shelters)
                        if scen.shelter_safe(sh) and T[a][s] <= inst.theta_max})
        if not cands:
            continue
        t, node = cands[0]
        load[node] = load.get(node, 0) + d
        person_min += d * t
    over = sum(max(0, l - site_cap[node]) for node, l in load.items())
    return {"load": load, "overflow": over, "person_minutes": person_min}


# ---------------------------------------------------------------------------
# Evacuation over time (Definitions 13 and 14, Algorithm 2)
# ---------------------------------------------------------------------------

def expanded_network(inst, scen, horizon, supplies, sink_caps):
    """Time-expanded network on steps 0..horizon.

    supplies: node -> persons available at time 0.
    sink_caps: shelter node -> total persons it may receive (None = no limit).
    """
    G = nx.DiGraph()
    nodes = inst.nodes
    for v in nodes:
        for t in range(horizon):
            G.add_edge((v, t), (v, t + 1))           # holdover, no capacity
    for (u, v, tau, cap, tag) in inst.open_arcs(scen.closed_tags):
        for t in range(0, horizon - tau + 1):
            G.add_edge((u, t), (v, t + tau), capacity=cap)
    for v, sup in supplies.items():
        if sup > 0:
            G.add_edge("S*", (v, 0), capacity=sup)
    for v, cap in sink_caps.items():
        for t in range(horizon + 1):
            G.add_edge((v, t), ("shel", v))
        if cap is None:
            G.add_edge(("shel", v), "Z*")
        else:
            G.add_edge(("shel", v), "Z*", capacity=cap)
    return G


def arrivals_by(inst, scen, horizon, supplies, sink_caps):
    """F(T): most evacuees who can reach shelters by time `horizon`."""
    if horizon < 0:
        return 0
    G = expanded_network(inst, scen, horizon, supplies, sink_caps)
    if "S*" not in G or "Z*" not in G:
        return 0
    return nx.maximum_flow_value(G, "S*", "Z*")


def plan_supplies(inst, plan):
    sup, caps = {}, {}
    for (a, k, cls), f in plan["x"].items():
        node = inst.origins[a]["node"]
        sup[node] = sup.get(node, 0) + f
        s = plan["slots"][k][0]
        snode = inst.shelters[s]["node"]
        caps[snode] = caps.get(snode, 0) + f
    return sup, caps


def reachable_total(inst, scen, supplies, sink_caps):
    """Most evacuees who can reach shelters with no time limit (connectivity only)."""
    G = nx.DiGraph()
    for (u, v, tau, cap, tag) in inst.open_arcs(scen.closed_tags):
        G.add_edge(u, v)
    for v, sup in supplies.items():
        if sup > 0:
            G.add_edge("S*", v, capacity=sup)
    for v, cap in sink_caps.items():
        if cap is None:
            G.add_edge(v, "Z*")
        else:
            G.add_edge(v, "Z*", capacity=cap)
    if "S*" not in G or "Z*" not in G:
        return 0
    return nx.maximum_flow_value(G, "S*", "Z*")


def clearance_time(inst, scen, supplies, sink_caps, t_hi=None):
    """Smallest T with F(T) = total supply, by doubling and bisection.

    Returns (inf, 0) when some evacuees cannot reach a shelter at all.
    """
    total = sum(supplies.values())
    if total == 0:
        return 0, 0
    if reachable_total(inst, scen, supplies, sink_caps) < total:
        return math.inf, 0
    if t_hi is None:
        t_hi = 8
        while arrivals_by(inst, scen, t_hi, supplies, sink_caps) < total:
            t_hi *= 2
            if t_hi > 1 << 16:
                return math.inf, 0
    lo, hi = -1, t_hi                      # F(lo) < total <= F(hi)
    calls = 0
    while hi - lo > 1:
        mid = (lo + hi) // 2
        calls += 1
        if arrivals_by(inst, scen, mid, supplies, sink_caps) >= total:
            hi = mid
        else:
            lo = mid
    return hi, calls


def static_rate(inst, scen, sources, sinks):
    """Static max flow c from all sources to all sinks (arc capacities only)."""
    G = nx.DiGraph()
    for (u, v, tau, cap, tag) in inst.open_arcs(scen.closed_tags):
        if G.has_edge(u, v):
            G[u][v]["capacity"] += cap
        else:
            G.add_edge(u, v, capacity=cap)
    for v in sources:
        G.add_edge("S*", v)
    for v in sinks:
        G.add_edge(v, "Z*")
    if "S*" not in G or "Z*" not in G:
        return 0
    return nx.maximum_flow_value(G, "S*", "Z*")


def clearance_lower_bound(inst, scen, supplies, sink_caps):
    """Proposition 7: T* >= tau_min - 1 + ceil(D / c), and T* >= farthest nearest."""
    total = sum(supplies.values())
    if total == 0:
        return 0
    adj = inst.adjacency(scen.closed_tags)
    srcs = [v for v, s in supplies.items() if s > 0]
    sinks = [v for v, c in sink_caps.items() if c is None or c > 0]
    tau_min = math.inf
    far = 0
    for v in srcs:
        dist = dijkstra(adj, v)
        near = min(dist.get(w, math.inf) for w in sinks)
        tau_min = min(tau_min, near)
        far = max(far, near)
    c = static_rate(inst, scen, srcs, sinks)
    if c == 0:
        return math.inf
    lb_cut = tau_min - 1 + math.ceil(total / c)
    return max(lb_cut, far)


# ---------------------------------------------------------------------------
# Siting new evacuation centers (Definition 16, Algorithm 3)
# ---------------------------------------------------------------------------

def coverage_value(inst, scen, T, theta, base_shelters, new_sites, site_cap):
    """Phi(B): persons who can be sheltered outside classrooms within theta.

    base_shelters: indices of existing shelters (their EC and open capacity
    count); new_sites: list of (node, capacity) for proposed centers.
    """
    G = nx.DiGraph()
    for a, o in enumerate(inst.origins):
        d = scen.demand(o)
        if d > 0:
            G.add_edge("SRC", ("o", a), capacity=d)
    for s in base_shelters:
        sh = inst.shelters[s]
        if not scen.shelter_safe(sh):
            continue
        cap = sh["cap_ec"] + sh["cap_open"]
        if cap <= 0:
            continue
        G.add_edge(("b", s), "SNK", capacity=cap)
        for a in range(len(inst.origins)):
            if G.has_node(("o", a)) and T[a][s] <= theta:
                G.add_edge(("o", a), ("b", s))
    for j, (node, dist_to) in enumerate(new_sites):
        G.add_edge(("n", j), "SNK", capacity=site_cap[j])
        for a in range(len(inst.origins)):
            if G.has_node(("o", a)) and dist_to[a] <= theta:
                G.add_edge(("o", a), ("n", j))
    if "SRC" not in G or "SNK" not in G:
        return 0
    return nx.maximum_flow_value(G, "SRC", "SNK")


class SitingProblem:
    """Coverage gain f(S) = Phi(E u S) - Phi(E) over candidate sites."""

    def __init__(self, inst, scen, theta, candidates, cand_cap):
        self.inst, self.scen, self.theta = inst, scen, theta
        self.T = travel_times(inst, scen)
        adj = inst.adjacency(scen.closed_tags)
        # time from each origin to each candidate node
        self.cand = []
        for node in candidates:
            dist_to = []
            for o in inst.origins:
                d = dijkstra(adj, o["node"]).get(node, math.inf)
                dist_to.append(d)
            self.cand.append((node, dist_to))
        self.cap = list(cand_cap)
        self.base = list(range(len(inst.shelters)))
        self._cache = {}
        self.phi0 = self.value(())

    def value(self, S):
        key = tuple(sorted(S))
        if key not in self._cache:
            sites = [self.cand[j] for j in key]
            caps = [self.cap[j] for j in key]
            self._cache[key] = coverage_value(self.inst, self.scen, self.T, self.theta,
                                              self.base, sites, caps)
        return self._cache[key]

    def gain(self, S):
        return self.value(S) - self.phi0


def greedy_sites(prob, k):
    chosen = []
    for _ in range(k):
        best, best_j = -1, None
        for j in range(len(prob.cand)):
            if j in chosen:
                continue
            g = prob.gain(chosen + [j])
            if g > best:
                best, best_j = g, j
        chosen.append(best_j)
    return chosen, prob.gain(chosen)


def best_sites(prob, k):
    best, arg = -1, None
    for S in itertools.combinations(range(len(prob.cand)), k):
        g = prob.gain(list(S))
        if g > best:
            best, arg = g, list(S)
    return arg, best
