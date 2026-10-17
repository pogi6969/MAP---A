/* LIGTA-S engine: the algorithms of "Safe Shelter, Open Schools" (Brimbuela, De Asis & Shin, 2026).
 *
 *   plan()          lexicographic shelter plan: max vulnerable placed, max placed, then
 *                   min persons in classrooms, min persons in school open spaces, min
 *                   person-minutes. Two maximum flows (Dinic), then one minimum-cost flow
 *                   whose arc costs are VECTORS compared lexicographically (successive
 *                   shortest paths with a queue-based Bellman-Ford). No big-M numbers.
 *   nearest()       baseline: everyone to the nearest safe shelter site, overflow counted.
 *   clearance()     exact clearance time on the time-expanded network (Ford & Fulkerson),
 *                   Dinic maximum flow, doubling then bisection; static lower bound.
 *   siting()        Ligtas Pinoy Center siting: coverage outside classrooms within a
 *                   travel-time standard, greedy choice (>= 63.2% of the best), exhaustive check.
 *
 * Plain ES5, no dependencies. Works in the browser (window.LigtasEngine) and in Node
 * (module.exports, or evaluated in a vm context by tests/verify.mjs).
 */
(function (root) {
  "use strict";

  var SPHERE_M2 = 3.5;            // covered living space per person (Sphere Handbook, 2018)
  var CLASSROOM_M2 = 63;          // DepEd standard classroom, 7 m x 9 m
  var Q = 18;                     // evacuees per classroom = floor(63 / 3.5)
  var TIER_EC = 0, TIER_OPEN = 1, TIER_ROOM = 2;
  var TIER_NAMES = ["non-school space", "school open space", "classroom"];
  var MAX_HORIZON = 1 << 15;      // clearance search gives up (reports "no finite time") beyond this

  /* ------------------------------------------------------------------ helpers */

  function capFromArea(area) {
    var a = +area;
    if (!(a > 0)) return 0;
    return Math.floor(a / SPHERE_M2 + 1e-9);
  }
  function toInt(v, dflt) {
    var n = Math.round(+v);
    return isFinite(n) ? n : (dflt || 0);
  }
  function setOf(list) {
    var s = {};
    (list || []).forEach(function (z) { if (z !== "" && z != null) s[String(z)] = true; });
    return s;
  }
  function meets(a, b) {
    for (var k in a) if (a.hasOwnProperty(k) && b[k]) return true;
    return false;
  }
  /* Tie-break between two node ids: as numbers when both are whole numbers, else as text
     (the same order the Python reference uses for integer and for named nodes). */
  function idLess(x, y) {
    var nx = /^-?\d+$/.test(x), ny = /^-?\d+$/.test(y);
    if (nx && ny) return +x < +y;
    return x < y;
  }

  /* ------------------------------------------------------------------ instance */

  /* data: {nodes:[{id,x,y}], roads:[{u,v,tau,cap,tag,oneWay?}], origins:[...], shelters:[...], thetaMax}
     opts.extraShelters: more shelters in the same format (e.g. new Ligtas Pinoy Centers). */
  function makeInstance(data, opts) {
    opts = opts || {};
    var nodes = (data.nodes || []).map(function (n) { return String(n.id); });
    var index = {};
    nodes.forEach(function (id, i) { index[id] = i; });
    var arcs = [];
    (data.roads || []).forEach(function (r) {
      var u = index[String(r.u)], v = index[String(r.v)];
      if (u === undefined || v === undefined || u === v) return;
      var tau = Math.max(1, toInt(r.tau, 1));
      var cap = Math.max(0, toInt(r.cap, 0));
      var tag = String(r.tag == null ? "" : r.tag);
      arcs.push({ u: u, v: v, tau: tau, cap: cap, tag: tag });
      if (!r.oneWay) arcs.push({ u: v, v: u, tau: tau, cap: cap, tag: tag });
    });
    var origins = (data.origins || []).filter(function (o) { return index[String(o.node)] !== undefined; })
      .map(function (o) {
        var pop = Math.max(0, toInt(o.pop));
        return { id: String(o.id), name: String(o.name || o.id), node: index[String(o.node)],
                 zones: setOf(o.zones), pop: pop, vul: Math.min(pop, Math.max(0, toInt(o.vul))) };
      });
    var shel = (data.shelters || []).concat(opts.extraShelters || []);
    var shelters = shel.filter(function (s) { return index[String(s.node)] !== undefined; })
      .map(function (s) {
        var school = s.kind === "school";
        return { id: String(s.id), name: String(s.name || s.id), node: index[String(s.node)],
                 kind: school ? "school" : "ec",
                 capEc: capFromArea(s.areaNonSchool),
                 capOpen: school ? capFromArea(s.areaOpen) : 0,
                 rooms: school ? Math.max(0, toInt(s.rooms)) : 0, q: Q,
                 learnersPerRoom: school ? Math.max(0, toInt(s.learnersPerRoom)) : 0,
                 accessible: s.accessible !== false && s.accessible !== "no" && s.accessible !== "false",
                 zones: setOf(s.zones) };
      });
    var theta = +(opts.thetaMax != null ? opts.thetaMax : data.thetaMax);
    return { nodes: nodes, index: index, arcs: arcs, origins: origins, shelters: shelters,
             thetaMax: theta > 0 ? theta : 1e9 };
  }

  function scenario(spec) {
    return { id: spec.id || "", name: spec.name || spec.id || "", zones: setOf(spec.zones), closed: setOf(spec.closed) };
  }
  function demand(o, sc) { return meets(o.zones, sc.zones) ? o.pop : 0; }
  function vulnerable(o, sc) { return meets(o.zones, sc.zones) ? o.vul : 0; }
  function shelterSafe(s, sc) { return !meets(s.zones, sc.zones); }
  function openArcs(inst, sc) { return inst.arcs.filter(function (e) { return !sc.closed[e.tag]; }); }

  /* ------------------------------------------------------------------ shortest paths */

  function adjacency(inst, sc) {
    var adj = inst.nodes.map(function () { return []; });
    openArcs(inst, sc).forEach(function (e) { adj[e.u].push(e); });
    return adj;
  }

  /* Dijkstra with a binary heap. Returns {dist, prev} (prev = arc used to reach each node). */
  function dijkstra(adj, src) {
    var n = adj.length, dist = new Array(n), prev = new Array(n), heap = [];
    for (var i = 0; i < n; i++) { dist[i] = Infinity; prev[i] = null; }
    dist[src] = 0;
    function push(d, v) {
      heap.push([d, v]);
      var c = heap.length - 1;
      while (c > 0) {
        var p = (c - 1) >> 1;
        if (heap[p][0] <= heap[c][0]) break;
        var t = heap[p]; heap[p] = heap[c]; heap[c] = t; c = p;
      }
    }
    function pop() {
      var top = heap[0], last = heap.pop();
      if (heap.length) {
        heap[0] = last;
        var c = 0;
        for (;;) {
          var l = 2 * c + 1, r = l + 1, m = c;
          if (l < heap.length && heap[l][0] < heap[m][0]) m = l;
          if (r < heap.length && heap[r][0] < heap[m][0]) m = r;
          if (m === c) break;
          var t = heap[m]; heap[m] = heap[c]; heap[c] = t; c = m;
        }
      }
      return top;
    }
    push(0, src);
    while (heap.length) {
      var it = pop(), d = it[0], u = it[1];
      if (d > dist[u]) continue;
      var out = adj[u];
      for (var k = 0; k < out.length; k++) {
        var e = out[k], nd = d + e.tau;
        if (nd < dist[e.v]) { dist[e.v] = nd; prev[e.v] = e; push(nd, e.v); }
      }
    }
    return { dist: dist, prev: prev };
  }

  /* T[a][s]: shortest minutes from origin a to shelter s on the open graph. */
  function travelTimes(inst, sc) {
    var adj = adjacency(inst, sc);
    return inst.origins.map(function (o) {
      var d = dijkstra(adj, o.node).dist;
      return inst.shelters.map(function (s) { return d[s.node]; });
    });
  }

  /* Node ids along the fastest open route from node a to node b ([] if none). */
  function route(inst, sc, fromNode, toNode) {
    var r = dijkstra(adjacency(inst, sc), fromNode);
    if (!isFinite(r.dist[toNode])) return { minutes: Infinity, path: [], arcs: [] };
    var path = [toNode], arcs = [], v = toNode;
    while (v !== fromNode) { var e = r.prev[v]; arcs.unshift(e); v = e.u; path.unshift(v); }
    return { minutes: r.dist[toNode], path: path.map(function (i) { return inst.nodes[i]; }), arcs: arcs };
  }

  /* ------------------------------------------------------------------ maximum flow (Dinic) */

  function Dinic(n) {
    this.n = n;
    this.head = new Int32Array(n).fill(-1);
    this.to = []; this.cap = []; this.next = [];
  }
  Dinic.prototype.add = function (u, v, c) {
    var e = this.to.length;
    this.to.push(v); this.cap.push(c); this.next.push(this.head[u]); this.head[u] = e;
    this.to.push(u); this.cap.push(0); this.next.push(this.head[v]); this.head[v] = e + 1;
    return e;
  };
  Dinic.prototype.flowOn = function (e) { return this.cap[e ^ 1]; };
  Dinic.prototype.run = function (s, t) {
    if (s === t) return 0;
    var n = this.n, head = this.head, to = this.to, cap = this.cap, next = this.next;
    var level = new Int32Array(n), it = new Int32Array(n), queue = new Int32Array(n);
    var total = 0;
    for (;;) {
      level.fill(-1);
      level[s] = 0;
      var qh = 0, qt = 0;
      queue[qt++] = s;
      while (qh < qt) {
        var u = queue[qh++];
        for (var e = head[u]; e !== -1; e = next[e]) {
          if (cap[e] > 0 && level[to[e]] < 0) { level[to[e]] = level[u] + 1; queue[qt++] = to[e]; }
        }
      }
      if (level[t] < 0) return total;
      for (var i = 0; i < n; i++) it[i] = head[i];
      /* iterative blocking-flow search: walk forward along level arcs, retreat from dead ends */
      var path = [];
      var x = s;
      for (;;) {
        if (x === t) {
          var f = Infinity, k;
          for (k = 0; k < path.length; k++) if (cap[path[k]] < f) f = cap[path[k]];
          if (f === Infinity) return Infinity;
          for (k = 0; k < path.length; k++) { cap[path[k]] -= f; cap[path[k] ^ 1] += f; }
          total += f;
          path.length = 0;
          x = s;
          continue;
        }
        var e2 = it[x];
        while (e2 !== -1 && !(cap[e2] > 0 && level[to[e2]] === level[x] + 1)) e2 = next[e2];
        it[x] = e2;
        if (e2 === -1) {
          if (x === s) break;
          level[x] = -1;                       // dead end: never enter it again this phase
          var back = path.pop();
          x = to[back ^ 1];
          it[x] = next[it[x]];
          continue;
        }
        path.push(e2);
        x = to[e2];
      }
    }
  };

  /* ------------------------------------------------------------------ min-cost flow, vector costs */

  function lexLess(a, ai, b, bi, dim) {
    for (var i = 0; i < dim; i++) {
      var x = a[ai + i], y = b[bi + i];
      if (x !== y) return x < y;
    }
    return false;
  }

  /* Successive shortest paths. Arc costs are integer vectors of length dim, ordered
     lexicographically (an ordered group, so shortest-path optimality conditions hold).
     Distances are found by a queue-based Bellman-Ford, which allows the negative
     costs of residual reverse arcs. */
  function VecMCF(n, dim) {
    this.n = n; this.dim = dim;
    this.head = new Int32Array(n).fill(-1);
    this.to = []; this.cap = []; this.next = []; this.cost = [];
  }
  VecMCF.prototype.add = function (u, v, c, costVec) {
    var e = this.to.length, d = this.dim;
    this.to.push(v); this.cap.push(c); this.next.push(this.head[u]); this.head[u] = e;
    this.to.push(u); this.cap.push(0); this.next.push(this.head[v]); this.head[v] = e + 1;
    for (var i = 0; i < d; i++) this.cost.push(costVec ? costVec[i] : 0);
    for (i = 0; i < d; i++) this.cost.push(costVec ? -costVec[i] : 0);
    return e;
  };
  VecMCF.prototype.flowOn = function (e) { return this.cap[e ^ 1]; };
  VecMCF.prototype.run = function (s, t, need) {
    var n = this.n, d = this.dim, head = this.head, to = this.to, cap = this.cap, next = this.next, cost = this.cost;
    var flow = 0, total = new Array(d).fill(0);
    var dist = new Float64Array(n * d), reach = new Uint8Array(n), inq = new Uint8Array(n);
    var prevE = new Int32Array(n), count = new Int32Array(n), cand = new Float64Array(d);
    while (flow < need) {
      reach.fill(0); inq.fill(0); count.fill(0); prevE.fill(-1);
      for (var i = 0; i < d; i++) dist[s * d + i] = 0;
      reach[s] = 1;
      var queue = [s], qh = 0;
      inq[s] = 1;
      while (qh < queue.length) {
        var u = queue[qh++];
        inq[u] = 0;
        for (var e = head[u]; e !== -1; e = next[e]) {
          if (!(cap[e] > 0)) continue;
          var v = to[e];
          for (i = 0; i < d; i++) cand[i] = dist[u * d + i] + cost[e * d + i];
          if (!reach[v] || lexLess(cand, 0, dist, v * d, d)) {
            for (i = 0; i < d; i++) dist[v * d + i] = cand[i];
            reach[v] = 1; prevE[v] = e;
            if (!inq[v]) {
              if (++count[v] > n + 1) throw new Error("negative cycle in residual network");
              inq[v] = 1; queue.push(v);
            }
          }
        }
        if (qh > 4096) { queue = queue.slice(qh); qh = 0; }
      }
      if (!reach[t]) break;
      var f = need - flow, x = t;
      while (x !== s) { e = prevE[x]; if (cap[e] < f) f = cap[e]; x = to[e ^ 1]; }
      x = t;
      while (x !== s) { e = prevE[x]; cap[e] -= f; cap[e ^ 1] += f; x = to[e ^ 1]; }
      for (i = 0; i < d; i++) total[i] += f * dist[t * d + i];
      flow += f;
    }
    return { flow: flow, cost: total };
  };

  /* ------------------------------------------------------------------ shelter slots */

  function slots(inst, sc, extraCaps) {
    var out = [];
    inst.shelters.forEach(function (sh, s) {
      if (!shelterSafe(sh, sc)) return;
      var add = (extraCaps && extraCaps[s]) || 0;
      if (sh.capEc + add > 0) out.push({ s: s, tier: TIER_EC, cap: sh.capEc + add, acc: sh.accessible });
      if (sh.capOpen > 0) out.push({ s: s, tier: TIER_OPEN, cap: sh.capOpen, acc: sh.accessible });
      if (sh.rooms > 0) out.push({ s: s, tier: TIER_ROOM, cap: sh.rooms * sh.q, acc: sh.accessible });
    });
    return out;
  }
  function suitable(inst, T, a, slot, isVul) {
    if (!(T[a][slot.s] <= inst.thetaMax)) return false;
    if (isVul && !slot.acc) return false;
    return true;
  }

  /* Maximum number placed: vulnerable only (classes "V") or everyone. */
  function maxPlaced(inst, sc, T, sl, withNon) {
    var nO = inst.origins.length, nS = sl.length;
    var SRC = 0, SNK = 1, oV = 2, oN = 2 + nO, sb = 2 + 2 * nO;
    var g = new Dinic(sb + nS);
    inst.origins.forEach(function (o, a) {
      var d = demand(o, sc), v = vulnerable(o, sc);
      if (v > 0) g.add(SRC, oV + a, v);
      if (withNon && d - v > 0) g.add(SRC, oN + a, d - v);
    });
    sl.forEach(function (slot, k) {
      g.add(sb + k, SNK, slot.cap);
      inst.origins.forEach(function (o, a) {
        var d = demand(o, sc), v = vulnerable(o, sc);
        if (v > 0 && suitable(inst, T, a, slot, true)) g.add(oV + a, sb + k, Infinity);
        if (withNon && d - v > 0 && suitable(inst, T, a, slot, false)) g.add(oN + a, sb + k, Infinity);
      });
    });
    return g.run(SRC, SNK);
  }

  /* policy "lex"  : school-preserving plan, costs (classroom, open space, minutes)
     policy "time" : time-only plan, costs (minutes, classroom, open space): travel first;
                     among equally fast plans, non-school space before school space. */
  function plan(inst, sc, policy, opts) {
    opts = opts || {};
    var T = opts.T || travelTimes(inst, sc);
    var sl = slots(inst, sc, opts.extraCaps);
    var fv = maxPlaced(inst, sc, T, sl, false);
    var ftot = maxPlaced(inst, sc, T, sl, true);
    var nO = inst.origins.length, nS = sl.length;
    var S = 0, SV = 1, SN = 2, oV = 3, oN = 3 + nO, sb = 3 + 2 * nO, SNK = sb + nS;
    var g = new VecMCF(SNK + 1, 3);
    g.add(S, SV, fv, null);
    g.add(S, SN, ftot - fv, null);
    var hasV = [], hasN = [];
    inst.origins.forEach(function (o, a) {
      var d = demand(o, sc), v = vulnerable(o, sc);
      hasV[a] = v > 0; hasN[a] = d - v > 0;
      if (hasV[a]) g.add(SV, oV + a, v, null);
      if (hasN[a]) g.add(SN, oN + a, d - v, null);
    });
    var pairs = [];
    sl.forEach(function (slot, k) {
      g.add(sb + k, SNK, slot.cap, null);
      inst.origins.forEach(function (o, a) {
        [["V", true], ["N", false]].forEach(function (c) {
          if (c[1] ? !hasV[a] : !hasN[a]) return;
          if (!suitable(inst, T, a, slot, c[1])) return;
          var t = T[a][slot.s];
          var room = slot.tier === TIER_ROOM ? 1 : 0, open = slot.tier === TIER_OPEN ? 1 : 0;
          var cv = policy === "time" ? [t, room, open] : [room, open, t];
          var e = g.add((c[1] ? oV : oN) + a, sb + k, Infinity, cv);
          pairs.push({ e: e, a: a, k: k, cls: c[0] });
        });
      });
    });
    var res = ftot > 0 ? g.run(S, SNK, ftot) : { flow: 0 };
    if (res.flow !== ftot) throw new Error("min-cost flow did not reach the maximum");
    var x = [];
    pairs.forEach(function (p) {
      var f = g.flowOn(p.e);
      if (f > 0) x.push({ a: p.a, k: p.k, cls: p.cls, f: f });
    });
    return summarize(inst, sc, T, sl, x, fv, ftot, policy);
  }

  function summarize(inst, sc, T, sl, x, fv, ftot, policy) {
    var byTier = [0, 0, 0], roomPersons = {}, load = {}, slotUse = sl.map(function () { return 0; });
    var pm = 0, maxT = 0;
    x.forEach(function (r) {
      var slot = sl[r.k], t = T[r.a][slot.s];
      byTier[slot.tier] += r.f;
      slotUse[r.k] += r.f;
      pm += r.f * t;
      if (t > maxT) maxT = t;
      load[slot.s] = (load[slot.s] || 0) + r.f;
      if (slot.tier === TIER_ROOM) roomPersons[slot.s] = (roomPersons[slot.s] || 0) + r.f;
    });
    var roomsClosed = {}, roomsTotal = 0, learners = 0;
    Object.keys(roomPersons).forEach(function (s) {
      var y = roomPersons[s];
      if (y <= 0) return;
      var sh = inst.shelters[+s];
      var k = Math.ceil(y / sh.q);              // pack each classroom full before opening the next
      roomsClosed[s] = k; roomsTotal += k; learners += k * sh.learnersPerRoom;
    });
    var D = 0, V = 0;
    inst.origins.forEach(function (o) { D += demand(o, sc); V += vulnerable(o, sc); });
    return { policy: policy, x: x, slots: sl, T: T, slotUse: slotUse,
             demand: D, vulnerable: V, vulPlaced: fv, placed: ftot, unplaced: D - ftot,
             personsEc: byTier[0], personsOpen: byTier[1], personsRoom: byTier[2],
             roomPersons: roomPersons, roomsClosed: roomsClosed, roomsClosedTotal: roomsTotal,
             learnersDisplaced: learners, personMinutes: pm,
             meanTime: ftot ? pm / ftot : 0, maxTime: maxT, load: load };
  }

  /* Baseline: every origin goes to its nearest safe, reachable shelter site (shelters
     sharing a road node form one site), whatever its capacity. */
  function nearest(inst, sc, opts) {
    opts = opts || {};
    var T = opts.T || travelTimes(inst, sc);
    var siteCap = {}, load = {}, pm = 0, moved = 0, choice = [];
    inst.shelters.forEach(function (sh) {
      if (shelterSafe(sh, sc)) siteCap[sh.node] = (siteCap[sh.node] || 0) + sh.capEc + sh.capOpen + sh.rooms * sh.q;
    });
    inst.origins.forEach(function (o, a) {
      var d = demand(o, sc);
      if (d === 0) { choice[a] = null; return; }
      var best = null;
      inst.shelters.forEach(function (sh, s) {
        if (!shelterSafe(sh, sc) || !(T[a][s] <= inst.thetaMax)) return;
        var c = [T[a][s], inst.nodes[sh.node], sh.node];
        if (!best || c[0] < best[0] || (c[0] === best[0] && idLess(c[1], best[1]))) best = c;
      });
      if (!best) { choice[a] = null; return; }
      choice[a] = { node: best[2], minutes: best[0], persons: d };
      load[best[2]] = (load[best[2]] || 0) + d;
      pm += d * best[0]; moved += d;
    });
    var over = 0, sites = [];
    Object.keys(load).forEach(function (node) {
      var cap = siteCap[node] || 0, ov = Math.max(0, load[node] - cap);
      over += ov;
      sites.push({ node: +node, id: inst.nodes[+node], load: load[node], cap: cap, overflow: ov });
    });
    return { load: load, overflow: over, personMinutes: pm, moved: moved,
             meanTime: moved ? pm / moved : 0, choice: choice, sites: sites };
  }

  /* ------------------------------------------------------------------ evacuation over time */

  /* supplies / sinks: {nodeIndex: persons}; sinks value null = no limit */
  function planSupplies(inst, p) {
    var sup = {}, caps = {};
    p.x.forEach(function (r) {
      var on = inst.origins[r.a].node, sn = inst.shelters[p.slots[r.k].s].node;
      sup[on] = (sup[on] || 0) + r.f;
      caps[sn] = (caps[sn] || 0) + r.f;
    });
    return { sup: sup, caps: caps };
  }
  function sumValues(o) { var t = 0; for (var k in o) if (o.hasOwnProperty(k)) t += o[k]; return t; }

  /* F(T): most evacuees inside shelters by minute H (time-expanded network). */
  function arrivalsBy(inst, sc, H, sup, caps) {
    if (H < 0) return 0;
    var N = inst.nodes.length, L = H + 1;
    var sinks = Object.keys(caps).map(Number);
    var SRC = N * L, SNK = SRC + 1, sh0 = SNK + 1;
    var g = new Dinic(sh0 + sinks.length);
    var v, t;
    for (v = 0; v < N; v++) for (t = 0; t < H; t++) g.add(v * L + t, v * L + t + 1, Infinity);
    openArcs(inst, sc).forEach(function (e) {
      if (e.cap <= 0) return;
      for (var t0 = 0; t0 + e.tau <= H; t0++) g.add(e.u * L + t0, e.v * L + t0 + e.tau, e.cap);
    });
    var any = false;
    Object.keys(sup).forEach(function (k) { if (sup[k] > 0) { g.add(SRC, (+k) * L, sup[k]); any = true; } });
    if (!any || !sinks.length) return 0;
    sinks.forEach(function (node, j) {
      for (var t1 = 0; t1 <= H; t1++) g.add(node * L + t1, sh0 + j, Infinity);
      g.add(sh0 + j, SNK, caps[node] == null ? Infinity : caps[node]);
    });
    return g.run(SRC, SNK);
  }

  /* Most evacuees who can reach their shelters with no time limit (connectivity only). */
  function reachableTotal(inst, sc, sup, caps) {
    var N = inst.nodes.length, SRC = N, SNK = N + 1;
    var g = new Dinic(N + 2);
    openArcs(inst, sc).forEach(function (e) { g.add(e.u, e.v, Infinity); });
    Object.keys(sup).forEach(function (k) { if (sup[k] > 0) g.add(SRC, +k, sup[k]); });
    Object.keys(caps).forEach(function (k) { g.add(+k, SNK, caps[k] == null ? Infinity : caps[k]); });
    return g.run(SRC, SNK);
  }

  /* Smallest H with F(H) = everyone: doubling from 8, then bisection (Algorithm 2). */
  function clearanceTime(inst, sc, sup, caps) {
    var total = sumValues(sup), calls = 0;
    if (total === 0) return { T: 0, calls: 0 };
    if (reachableTotal(inst, sc, sup, caps) < total) return { T: Infinity, calls: 0, cutOff: true };
    var hi = 8;
    for (;;) {
      calls++;
      if (arrivalsBy(inst, sc, hi, sup, caps) >= total) break;
      hi *= 2;
      if (hi > MAX_HORIZON) return { T: Infinity, calls: calls, tooLong: true };
    }
    var lo = -1;
    while (hi - lo > 1) {
      var mid = Math.floor((lo + hi) / 2);
      calls++;
      if (arrivalsBy(inst, sc, mid, sup, caps) >= total) hi = mid; else lo = mid;
    }
    return { T: hi, calls: calls };
  }

  /* Static maximum flow from all sending origins to all receiving shelters (arc capacities only). */
  function staticRate(inst, sc, sources, sinks) {
    var N = inst.nodes.length, SRC = N, SNK = N + 1;
    var g = new Dinic(N + 2), merged = {};
    openArcs(inst, sc).forEach(function (e) {
      var key = e.u + ">" + e.v;
      merged[key] = (merged[key] || 0) + e.cap;
    });
    Object.keys(merged).forEach(function (key) {
      var p = key.split(">");
      g.add(+p[0], +p[1], merged[key]);
    });
    sources.forEach(function (v) { g.add(SRC, v, Infinity); });
    sinks.forEach(function (v) { g.add(v, SNK, Infinity); });
    return g.run(SRC, SNK);
  }

  /* Proposition 8: T* >= max(tau_min - 1 + ceil(D'/c), farthest of the nearest shelters). */
  function clearanceLowerBound(inst, sc, sup, caps) {
    var total = sumValues(sup);
    if (total === 0) return 0;
    var adj = adjacency(inst, sc);
    var srcs = Object.keys(sup).filter(function (k) { return sup[k] > 0; }).map(Number);
    var sinks = Object.keys(caps).filter(function (k) { return caps[k] == null || caps[k] > 0; }).map(Number);
    var tauMin = Infinity, far = 0;
    srcs.forEach(function (v) {
      var dist = dijkstra(adj, v).dist, near = Infinity;
      sinks.forEach(function (w) { if (dist[w] < near) near = dist[w]; });
      if (near < tauMin) tauMin = near;
      if (near > far) far = near;
    });
    var c = staticRate(inst, sc, srcs, sinks);
    if (c === 0) return Infinity;
    var cut = tauMin - 1 + Math.ceil(total / c);
    return Math.max(cut, far);
  }

  function arrivalCurve(inst, sc, sup, caps, until, step) {
    var out = [];
    step = step || 2;
    for (var t = 0; t <= until; t += step) out.push([t, arrivalsBy(inst, sc, t, sup, caps)]);
    return out;
  }

  /* Plan + clearance time + lower bound in one call. */
  function evaluate(inst, sc, policy, opts) {
    var p = plan(inst, sc, policy, opts);
    var sc2 = planSupplies(inst, p);
    var ct = clearanceTime(inst, sc, sc2.sup, sc2.caps);
    p.clearance = ct.T; p.clearanceCalls = ct.calls;
    p.clearanceLB = clearanceLowerBound(inst, sc, sc2.sup, sc2.caps);
    p.supplies = sc2;
    return p;
  }

  /* ------------------------------------------------------------------ siting */

  function coverageValue(inst, sc, T, theta, newSites) {
    var nO = inst.origins.length, nB = inst.shelters.length, nN = newSites.length;
    var SRC = 0, SNK = 1, ob = 2, bb = 2 + nO, nb = 2 + nO + nB;
    var g = new Dinic(nb + nN), anyO = false, anyS = false;
    var dem = inst.origins.map(function (o) { return demand(o, sc); });
    dem.forEach(function (d, a) { if (d > 0) { g.add(SRC, ob + a, d); anyO = true; } });
    inst.shelters.forEach(function (sh, s) {
      if (!shelterSafe(sh, sc)) return;
      var cap = sh.capEc + sh.capOpen;
      if (cap <= 0) return;
      g.add(bb + s, SNK, cap); anyS = true;
      for (var a = 0; a < nO; a++) if (dem[a] > 0 && T[a][s] <= theta) g.add(ob + a, bb + s, Infinity);
    });
    newSites.forEach(function (site, j) {
      g.add(nb + j, SNK, site.cap); anyS = true;
      for (var a = 0; a < nO; a++) if (dem[a] > 0 && site.distTo[a] <= theta) g.add(ob + a, nb + j, Infinity);
    });
    if (!anyO || !anyS) return 0;
    return g.run(SRC, SNK);
  }

  /* candidates: [{node (id), name, area}] ; f(S) = Phi(E u S) - Phi(E) */
  function SitingProblem(inst, sc, theta, candidates) {
    this.inst = inst; this.sc = sc; this.theta = theta;
    this.T = travelTimes(inst, sc);
    var adj = adjacency(inst, sc);
    var fromOrigin = inst.origins.map(function (o) { return dijkstra(adj, o.node).dist; });
    this.cand = candidates.map(function (c) {
      var node = inst.index[String(c.node)];
      return { node: node, id: String(c.node), name: c.name || String(c.node), area: +c.area || 0,
               cap: capFromArea(c.area),
               distTo: fromOrigin.map(function (d) { return node === undefined ? Infinity : d[node]; }) };
    });
    this.cache = {};
    this.phi0 = this.value([]);
  }
  SitingProblem.prototype.value = function (S) {
    var key = S.slice().sort(function (a, b) { return a - b; }).join(",");
    if (!(key in this.cache)) {
      var self = this;
      this.cache[key] = coverageValue(this.inst, this.sc, this.T, this.theta,
        S.slice().sort(function (a, b) { return a - b; }).map(function (j) { return self.cand[j]; }));
    }
    return this.cache[key];
  };
  SitingProblem.prototype.gain = function (S) { return this.value(S) - this.phi0; };
  SitingProblem.prototype.greedy = function (k) {
    var chosen = [], gains = [];
    for (var r = 0; r < k && chosen.length < this.cand.length; r++) {
      var best = -1, bj = -1;
      for (var j = 0; j < this.cand.length; j++) {
        if (chosen.indexOf(j) >= 0) continue;
        var g = this.gain(chosen.concat([j]));
        if (g > best) { best = g; bj = j; }
      }
      chosen.push(bj); gains.push(best);
    }
    return { sites: chosen, gains: gains };
  };
  SitingProblem.prototype.best = function (k) {
    var n = this.cand.length, best = -1, arg = null, idx = [], self = this, evals = 0;
    if (k > n) return null;
    for (var i = 0; i < k; i++) idx.push(i);
    for (;;) {
      var g = self.gain(idx); evals++;
      if (g > best) { best = g; arg = idx.slice(); }
      var p = k - 1;
      while (p >= 0 && idx[p] === n - k + p) p--;
      if (p < 0) break;
      idx[p]++;
      for (var q = p + 1; q < k; q++) idx[q] = idx[q - 1] + 1;
    }
    return { sites: arg, gain: best, evals: evals };
  };

  function binom(n, k) { var r = 1; for (var i = 1; i <= k; i++) r = r * (n - k + i) / i; return Math.round(r); }

  /* Full siting study: greedy order, exhaustive best (when small), and the recomputed plan. */
  function siting(data, scSpec, theta, candidates, kMax, opts) {
    opts = opts || {};
    var inst = makeInstance(data, opts);
    var sc = scenario(scSpec);
    var prob = new SitingProblem(inst, sc, theta, candidates);
    kMax = Math.min(kMax, prob.cand.length);
    var order = prob.greedy(kMax);
    var rows = [];
    for (var k = 1; k <= kMax; k++) {
      var S = order.sites.slice(0, k);
      var best = binom(prob.cand.length, k) <= (opts.maxExhaustive || 5000) ? prob.best(k) : null;
      var extra = S.map(function (j) {
        var c = prob.cand[j];
        return { id: "LPC-" + c.id, name: c.name, node: c.id, kind: "ec", areaNonSchool: c.area,
                 areaOpen: 0, rooms: 0, learnersPerRoom: 0, accessible: true, zones: [] };
      });
      var inst2 = makeInstance(data, { extraShelters: extra, thetaMax: opts.thetaMax });
      var p2 = evaluate(inst2, sc, "lex");
      rows.push({ k: k, sites: S.map(function (j) { return prob.cand[j].id; }), gain: prob.gain(S),
                  bestSites: best ? best.sites.map(function (j) { return prob.cand[j].id; }) : null,
                  bestGain: best ? best.gain : null,
                  unplaced: p2.unplaced, personsRoom: p2.personsRoom, roomsClosed: p2.roomsClosedTotal,
                  learners: p2.learnersDisplaced, clearance: p2.clearance, meanTime: p2.meanTime });
    }
    var single = {};
    prob.cand.forEach(function (c, j) { single[c.id] = prob.gain([j]); });
    return { theta: theta, phi0: prob.phi0, candidates: prob.cand.map(function (c) { return { id: c.id, name: c.name, cap: c.cap, area: c.area }; }),
             rows: rows, singleGains: single, guarantee: 1 - Math.pow(1 - 1 / Math.max(1, kMax), kMax) };
  }

  /* ------------------------------------------------------------------ closures */

  /* Closing groups of road tags under one scenario: the plan held fixed (Definition 12)
     and a fresh plan for the damaged network. */
  function closureStudy(data, scSpec, groups, opts) {
    opts = opts || {};
    var inst = makeInstance(data, opts);
    var base = scenario(scSpec);
    var p0 = plan(inst, base, "lex");
    var s0 = planSupplies(inst, p0);
    var t0 = clearanceTime(inst, base, s0.sup, s0.caps).T;
    return groups.map(function (gr) {
      var sc = scenario({ id: base.id, zones: Object.keys(base.zones), closed: Object.keys(base.closed).concat(gr.tags) });
      var tf = clearanceTime(inst, sc, s0.sup, s0.caps).T;
      var p = plan(inst, sc, "lex");
      var s2 = planSupplies(inst, p);
      var tn = clearanceTime(inst, sc, s2.sup, s2.caps).T;
      return { name: gr.name, tags: gr.tags.slice(), clearanceOpen: t0, clearanceFixedPlan: tf,
               delta: tf - t0, unplaced: p.unplaced, personsRoom: p.personsRoom,
               roomsClosed: p.roomsClosedTotal, clearanceNewPlan: tn,
               meanTime: p.meanTime, maxTime: p.maxTime };
    });
  }

  var api = {
    version: "1.0.0",
    SPHERE_M2: SPHERE_M2, CLASSROOM_M2: CLASSROOM_M2, Q: Q, TIER_NAMES: TIER_NAMES,
    capFromArea: capFromArea, makeInstance: makeInstance, scenario: scenario,
    demand: demand, vulnerable: vulnerable, shelterSafe: shelterSafe,
    travelTimes: travelTimes, route: route, slots: slots,
    plan: plan, nearest: nearest, evaluate: evaluate, planSupplies: planSupplies,
    arrivalsBy: arrivalsBy, clearanceTime: clearanceTime, clearanceLowerBound: clearanceLowerBound,
    arrivalCurve: arrivalCurve, coverageValue: coverageValue, SitingProblem: SitingProblem,
    siting: siting, closureStudy: closureStudy, Dinic: Dinic, VecMCF: VecMCF
  };
  root.LigtasEngine = api;
  if (typeof module === "object" && module.exports) module.exports = api;
})(typeof globalThis !== "undefined" ? globalThis : (typeof window !== "undefined" ? window : this));
