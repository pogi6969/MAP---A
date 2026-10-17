/* LIGTA-S app: the user interface around LigtasEngine (algorithms) and LigtasMap (drawing). */
(function () {
  "use strict";
  var E = window.LigtasEngine, M = window.LigtasMap;
  var DEMO = JSON.parse(document.getElementById("ligtas-demo").textContent);
  var KEY_DATA = "ligtas.data.v1", KEY_UI = "ligtas.ui.v1";
  var $ = function (id) { return document.getElementById(id); };
  var qa = function (sel, el) { return Array.prototype.slice.call((el || document).querySelectorAll(sel)); };

  function clone(x) { return JSON.parse(JSON.stringify(x)); }
  function fmt(n) { return n === Infinity ? "∞" : (n == null || isNaN(n)) ? "–" : Math.round(n).toLocaleString("en-US"); }
  function fmt2(n) { return (Math.round(n * 100) / 100).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
  function esc(s) { return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;"); }
  function minutes(n) { return n === Infinity || n == null ? "no finite time" : fmt(n) + " min"; }

  /* ---------------------------------------------------------------- storage */
  var storageOK = true;
  function load(key) {
    try { var s = localStorage.getItem(key); return s ? JSON.parse(s) : null; } catch (e) { storageOK = false; return null; }
  }
  function store(key, val) {
    try { localStorage.setItem(key, JSON.stringify(val)); return true; } catch (e) { storageOK = false; return false; }
  }
  function drop(key) { try { localStorage.removeItem(key); } catch (e) { /* nothing to do */ } }

  function validData(d) {
    return d && typeof d === "object" && Array.isArray(d.nodes) && Array.isArray(d.roads) && Array.isArray(d.origins) && Array.isArray(d.shelters);
  }
  function normalize(d) {
    d = clone(d);
    ["scenarios", "channels", "zones", "candidates"].forEach(function (k) { if (!Array.isArray(d[k])) d[k] = clone(DEMO[k] || []); });
    if (!d.geo && d.synthetic) d.geo = clone(DEMO.geo);
    if (!(+d.thetaMax > 0)) d.thetaMax = DEMO.thetaMax;
    if (!(+d.thetaSite > 0)) d.thetaSite = DEMO.thetaSite;
    return d;
  }

  var saved = load(KEY_DATA);
  var S = {
    data: validData(saved) ? normalize(saved) : clone(DEMO),
    edited: validData(saved),
    rev: 0,
    cache: {},
    ui: Object.assign({ tab: "plan", scen: "AL3", theta: null, days: 15, rule: "lex", theme: "auto",
                        resOrigin: null, resVul: false, resScen: "AL3", extra: [], siteScen: "AL4+L",
                        siteTheta: null, siteK: 3, siteRow: null }, load(KEY_UI) || {})
  };
  if (!(S.ui.theta > 0)) S.ui.theta = S.data.thetaMax;
  if (!(S.ui.siteTheta > 0)) S.ui.siteTheta = S.data.thetaSite || 30;
  function saveUI() { store(KEY_UI, S.ui); }
  function saveData() {
    S.rev++; S.cache = {};
    S.edited = true;
    var ok = store(KEY_DATA, S.data);
    setSaveStatus(ok ? "Saved in this browser." : "Could not save in this browser (private mode or storage blocked). Export to keep your edits.");
    banner();
  }
  function setSaveStatus(t) { var el = $("save-status"); if (el) el.textContent = t; }

  /* ---------------------------------------------------------------- engine helpers */
  function scenById(id) {
    var list = S.data.scenarios || [];
    for (var i = 0; i < list.length; i++) if (list[i].id === id) return list[i];
    return list[0] || { id: "none", name: "No scenario", zones: [], closed: [] };
  }
  function inst(opts) { return E.makeInstance(S.data, Object.assign({ thetaMax: S.ui.theta }, opts || {})); }
  function cached(key, fn) {
    var k = S.rev + "|" + S.ui.theta + "|" + key;
    if (!(k in S.cache)) S.cache[k] = fn();
    return S.cache[k];
  }
  function planFor(scenId, rule, extraClosed) {
    var sp = scenById(scenId);
    var spec = { id: sp.id, name: sp.name, zones: sp.zones, closed: (sp.closed || []).concat(extraClosed || []) };
    return cached("plan|" + scenId + "|" + rule + "|" + (extraClosed || []).join(","), function () {
      var I = inst(), sc = E.scenario(spec);
      if (rule === "near") { var n = E.nearest(I, sc); n.inst = I; n.sc = sc; n.rule = rule; return n; }
      var p = E.evaluate(I, sc, rule);
      p.inst = I; p.sc = sc; p.rule = rule;
      return p;
    });
  }
  /* persons from each origin to each shelter, with the route on the open roads */
  function flowsOf(p) {
    var I = p.inst, out = [], pairs = {};
    if (p.rule === "near") {
      p.choice.forEach(function (c, a) {
        if (!c) return;
        var r = E.route(I, p.sc, I.origins[a].node, c.node);
        out.push({ path: r.path, persons: c.persons, title: I.origins[a].id + " to " + I.nodes[c.node] + ": " + fmt(c.persons) + " evacuees, " + c.minutes + " min" });
      });
      return out;
    }
    p.x.forEach(function (r) {
      var s = p.slots[r.k].s, key = r.a + ">" + s;
      if (!pairs[key]) pairs[key] = { a: r.a, s: s, persons: 0, room: 0 };
      pairs[key].persons += r.f;
      if (p.slots[r.k].tier === 2) pairs[key].room += r.f;
    });
    Object.keys(pairs).forEach(function (k) {
      var q = pairs[k], o = I.origins[q.a], sh = I.shelters[q.s];
      var r = E.route(I, p.sc, o.node, sh.node);
      out.push({ path: r.path, persons: q.persons, tone: q.room === q.persons ? "room" : "",
                 title: o.id + " to " + sh.id + ": " + fmt(q.persons) + " evacuees, " + p.T[q.a][q.s] + " min" + (q.room ? " (" + fmt(q.room) + " in classrooms)" : "") });
    });
    return out;
  }
  function siteNotesOf(p) {
    var I = p.inst, notes = {};
    if (p.rule === "near") {
      p.sites.forEach(function (s) {
        notes[s.id] = s.overflow > 0 ? { text: fmt(s.load) + " sent, " + fmt(s.overflow) + " over", tone: "over" } : { text: fmt(s.load) + " sent" };
      });
      return notes;
    }
    var byNode = {};
    I.shelters.forEach(function (sh, s) {
      var id = I.nodes[sh.node];
      if (!byNode[id]) byNode[id] = { load: 0, rooms: 0 };
      byNode[id].load += p.load[s] || 0;
      byNode[id].rooms += p.roomsClosed[s] || 0;
    });
    Object.keys(byNode).forEach(function (id) {
      var b = byNode[id];
      if (b.load > 0) notes[id] = b.rooms > 0 ? { text: fmt(b.load) + " · " + b.rooms + " rooms", tone: "room" } : { text: fmt(b.load) + "" };
    });
    return notes;
  }
  function mapLabel(prefix, sp) { return prefix + " " + sp.name + ". Test network E1, synthetic."; }

  /* ---------------------------------------------------------------- shell: tabs, theme, banner */
  var TABS = ["plan", "clear", "site", "res", "cap", "data"];
  function showTab(t, focus) {
    if (TABS.indexOf(t) < 0) t = "plan";
    S.ui.tab = t; saveUI();
    qa(".tab").forEach(function (b) {
      var on = b.getAttribute("data-tab") === t;
      b.setAttribute("aria-selected", on ? "true" : "false");
      b.tabIndex = on ? 0 : -1;
      if (on && focus) b.focus();
    });
    TABS.forEach(function (x) { $("view-" + x).hidden = x !== t; });
    if (location.hash !== "#" + t) { try { history.replaceState(null, "", "#" + t); } catch (e) { /* file: or sandbox */ } }
    render();
  }
  qa(".tab").forEach(function (b, i, all) {
    b.addEventListener("click", function () { showTab(b.getAttribute("data-tab")); window.scrollTo(0, 0); });
    b.addEventListener("keydown", function (e) {
      var j = e.key === "ArrowRight" ? (i + 1) % all.length : e.key === "ArrowLeft" ? (i - 1 + all.length) % all.length : e.key === "Home" ? 0 : e.key === "End" ? all.length - 1 : -1;
      if (j < 0) return;
      e.preventDefault();
      showTab(all[j].getAttribute("data-tab"), true);
    });
  });
  window.addEventListener("hashchange", function () { var h = location.hash.slice(1); if (TABS.indexOf(h) >= 0 && h !== S.ui.tab) showTab(h); });

  function applyTheme() {
    var t = S.ui.theme;
    if (t === "auto") document.documentElement.removeAttribute("data-theme"); else document.documentElement.setAttribute("data-theme", t);
    var b = $("theme-btn"), name = { auto: "automatic", light: "light", dark: "dark" }[t];
    b.setAttribute("aria-label", "Color theme: " + name + ". Change theme.");
    b.title = "Theme: " + name;
    b.querySelector("use").setAttribute("href", t === "auto" ? "#i-auto" : t === "dark" ? "#i-moon" : "#i-sun");
  }
  $("theme-btn").addEventListener("click", function () {
    S.ui.theme = { auto: "light", light: "dark", dark: "auto" }[S.ui.theme] || "auto";
    saveUI(); applyTheme();
  });
  var about = $("about");
  $("about-btn").addEventListener("click", function () { if (about.showModal) about.showModal(); else about.setAttribute("open", ""); });
  $("about-close").addEventListener("click", function () { if (about.close) about.close(); else about.removeAttribute("open"); });
  about.addEventListener("click", function (e) { if (e.target === about && about.close) about.close(); });

  function banner() {
    var b = $("banner"), t = $("banner-text");
    if (!S.edited && S.data.synthetic) {
      b.className = "banner";
      t.textContent = "Demo data: test network E1, a synthetic volcano. Not real Albay data; every number here comes from this test network.";
    } else if (S.data.synthetic) {
      b.className = "banner";
      t.textContent = "Edited copy of test network E1 (synthetic). Not real Albay data. Reset it from the Data tab.";
    } else {
      b.className = "banner user";
      t.textContent = "Your own data. LIGTA-S is a planning aid; results are only as good as the data entered.";
    }
  }
  var toastT = null;
  function toast(msg) {
    var el = $("toast");
    el.textContent = msg; el.hidden = false;
    clearTimeout(toastT);
    toastT = setTimeout(function () { el.hidden = true; }, 3200);
  }

  /* scenario switches */
  function shortName(sp) {
    var narrow = window.matchMedia && window.matchMedia("(max-width: 420px)").matches;
    if (!narrow) return sp.name;
    return sp.name.replace("Alert Level", "AL").replace(" + lahar", " + lahar");
  }
  function drawSeg(el, cur, onPick) {
    el.innerHTML = (S.data.scenarios || []).map(function (sp) {
      return '<button type="button" data-id="' + esc(sp.id) + '" aria-pressed="' + (sp.id === cur ? "true" : "false") + '" title="' + esc(sp.name + ": zones " + sp.zones.join(", ") + (sp.closed && sp.closed.length ? "; closed " + sp.closed.join(", ") : "")) + '">' + esc(shortName(sp)) + '</button>';
    }).join("");
    qa("button", el).forEach(function (b) { b.onclick = function () { onPick(b.getAttribute("data-id")); }; });
  }

  /* ---------------------------------------------------------------- PLANNER */
  var busy = false;
  function later(fn) { setTimeout(function () { try { fn(); } catch (e) { console.error(e); toast("Something went wrong: " + e.message); } }, 16); }

  function renderPlan() {
    qa(".scen-seg").forEach(function (el) {
      drawSeg(el, S.ui.scen, function (id) { S.ui.scen = id; S.ui.extra = []; saveUI(); render(); });
    });
    $("theta").value = S.ui.theta;
    $("days").value = S.ui.days;
    qa("[data-rule]").forEach(function (b) {
      var on = b.getAttribute("data-rule") === S.ui.rule;
      b.setAttribute("aria-pressed", on ? "true" : "false");
      b.className = "btn" + (on ? " teal" : "");
    });
    var box = $("plan-result");
    box.classList.add("computing");
    later(function () {
      var sp = scenById(S.ui.scen);
      var p;
      try { p = planFor(S.ui.scen, S.ui.rule); } catch (e) { box.classList.remove("computing"); box.innerHTML = '<p class="err">Could not compute: ' + esc(e.message) + '</p>'; return; }
      box.classList.remove("computing");
      box.innerHTML = S.ui.rule === "near" ? nearHTML(p, sp) : planHTML(p, sp);
      M.draw($("map-plan"), S.data, { scenario: sp, flows: flowsOf(p), siteNotes: siteNotesOf(p), label: mapLabel(ruleName(S.ui.rule) + ",", sp) });
      $("plan-detail").innerHTML = S.ui.rule === "near" ? nearDetail(p) : planDetail(p);
      $("plan-detail-pill").textContent = ruleName(S.ui.rule);
      renderCompare();
    });
  }
  function ruleName(r) { return r === "lex" ? "School-preserving plan" : r === "time" ? "Time-only plan" : "Nearest-site rule"; }

  function tierBar(p) {
    var D = p.demand || 1;
    var parts = [["t-ec", p.personsEc, "Non-school space"], ["t-open", p.personsOpen, "School open space"], ["t-room", p.personsRoom, "Classrooms"], ["t-none", p.unplaced, "Not placed"]];
    return '<div class="tierbar" role="img" aria-label="' + parts.map(function (x) { return x[2] + " " + fmt(x[1]); }).join(", ") + '">' +
      parts.map(function (x) { return x[1] > 0 ? '<i class="' + x[0] + '" style="width:' + (100 * x[1] / D).toFixed(3) + '%"></i>' : ""; }).join("") + '</div>' +
      '<div class="tierlegend">' + parts.map(function (x) { return '<div><i class="sw ' + x[0] + '"></i><span>' + x[2] + '<b>' + fmt(x[1]) + '</b></span></div>'; }).join("") + '</div>';
  }
  function planHTML(p, sp) {
    var I = p.inst, days = Math.max(0, +S.ui.days || 0);
    var schools = Object.keys(p.roomsClosed).map(function (s) {
      var sh = I.shelters[+s];
      return { id: sh.id, name: sh.name, rooms: p.roomsClosed[s], persons: p.roomPersons[s], learners: p.roomsClosed[s] * sh.learnersPerRoom, of: sh.rooms };
    });
    var h = '<div class="res-title"><h2>' + ruleName(p.rule) + '</h2><span class="pill ' + (p.rule === "lex" ? "teal" : "") + '">' + esc(sp.name) + '</span>' +
      (p.rule === "lex" ? '<span class="pill gold">exact optimum</span>' : "") + '</div>';
    h += '<div class="kpis">' +
      '<div class="kpi ' + (p.roomsClosedTotal ? "bad" : "good") + '"><b>' + fmt(p.roomsClosedTotal) + '</b><span>classrooms closed</span></div>' +
      '<div class="kpi ' + (p.learnersDisplaced ? "bad" : "good") + '"><b>' + fmt(p.learnersDisplaced) + '</b><span>learners displaced</span></div>' +
      '<div class="kpi"><b>' + fmt(p.roomsClosedTotal * days) + '</b><span>classroom-days (' + fmt(days) + ' days)</span></div>' +
      '<div class="kpi ' + (p.unplaced ? "bad" : "good") + '"><b>' + fmt(p.unplaced) + '</b><span>evacuees not placed</span></div></div>';
    h += tierBar(p);
    h += '<dl class="stats">' +
      '<div><dt>Evacuees</dt><dd>' + fmt(p.demand) + '</dd></div>' +
      '<div><dt>Vulnerable placed</dt><dd>' + fmt(p.vulPlaced) + ' of ' + fmt(p.vulnerable) + '</dd></div>' +
      '<div><dt>Mean trip</dt><dd>' + fmt2(p.meanTime) + ' min</dd></div>' +
      '<div><dt>Longest trip</dt><dd>' + fmt(p.maxTime) + ' min</dd></div>' +
      '<div><dt>Person-minutes</dt><dd>' + fmt(p.personMinutes) + '</dd></div>' +
      '<div><dt>Clearance time</dt><dd>' + minutes(p.clearance) + '</dd></div></dl>';
    if (schools.length) {
      h += '<h3>Classrooms closed, packed 18 per room</h3><ul class="small" style="margin:0;padding-left:1.1rem">' + schools.map(function (s) {
        return '<li><b>' + esc(s.id) + '</b> ' + esc(s.name) + ': ' + fmt(s.persons) + ' evacuees in ' + s.rooms + ' of ' + s.of + ' rooms, ' + fmt(s.learners) + ' learners out of class</li>';
      }).join("") + '</ul>';
    } else if (p.placed > 0) {
      h += '<p class="note ok">No classroom is used: every evacuee fits in non-school space or school open space.</p>';
    }
    if (p.unplaced > 0) h += '<p class="note warn">' + fmt(p.unplaced) + ' evacuees cannot be placed within ' + fmt(S.ui.theta) + ' minutes in any shelter that is open and safe in this scenario.</p>';
    if (p.rule === "time") {
      var lx = planFor(S.ui.scen, "lex");
      var dm = p.meanTime ? (lx.meanTime - p.meanTime) : 0;
      h += '<p class="note">The school-preserving plan closes ' + fmt(lx.roomsClosedTotal) + ' classrooms instead of ' + fmt(p.roomsClosedTotal) + ' (' + fmt(lx.learnersDisplaced) + ' learners displaced instead of ' + fmt(p.learnersDisplaced) + '), with a mean trip ' + fmt2(Math.abs(dm)) + ' min ' + (dm >= 0 ? "longer" : "shorter") + '.</p>';
    }
    return h;
  }
  function nearHTML(p, sp) {
    var over = p.sites.filter(function (s) { return s.overflow > 0; });
    var h = '<div class="res-title"><h2>Nearest-site rule</h2><span class="pill">' + esc(sp.name) + '</span><span class="pill">baseline</span></div>';
    h += '<div class="kpis">' +
      '<div class="kpi ' + (p.overflow ? "bad" : "good") + '"><b>' + fmt(p.overflow) + '</b><span>arrive at full shelters</span></div>' +
      '<div class="kpi"><b>' + fmt(over.length) + '</b><span>sites over capacity</span></div>' +
      '<div class="kpi"><b>' + fmt2(p.meanTime) + '</b><span>mean trip (min)</span></div>' +
      '<div class="kpi"><b>' + fmt(p.moved) + '</b><span>evacuees sent</span></div></div>';
    h += '<p class="small muted">Everyone goes to the closest open shelter site, whatever its capacity, accessibility or classrooms. Capacity here counts every space at the site, classrooms included.</p>';
    if (p.overflow > 0) h += '<p class="note warn">' + fmt(p.overflow) + ' evacuees arrive at shelters that are already full, and must be moved again.</p>';
    return h;
  }
  function planDetail(p) {
    var I = p.inst, rows = {};
    p.x.forEach(function (r) {
      var sl = p.slots[r.k], k = r.a + "|" + sl.s + "|" + sl.tier + "|" + r.cls;
      if (!rows[k]) rows[k] = { a: r.a, s: sl.s, tier: sl.tier, cls: r.cls, f: 0 };
      rows[k].f += r.f;
    });
    var list = Object.keys(rows).map(function (k) { return rows[k]; }).sort(function (x, y) { return x.a - y.a || x.s - y.s || x.tier - y.tier || (x.cls < y.cls ? 1 : -1); });
    if (!list.length) return '<p class="muted small">Nobody needs to move in this scenario.</p>';
    var tierName = ["Non-school space", "School open space", "Classroom"];
    var unpl = unplacedByOrigin(p);
    return '<table><thead><tr><th>Origin</th><th>Group</th><th>Shelter</th><th>Space</th><th class="n">Persons</th><th class="n">Minutes</th></tr></thead><tbody>' +
      list.map(function (r) {
        var o = I.origins[r.a], sh = I.shelters[r.s];
        return '<tr><td><b>' + esc(o.id) + '</b></td><td>' + (r.cls === "V" ? "Vulnerable" : "Others") + '</td><td>' + esc(sh.id) + ' <span class="muted">' + esc(sh.name) + '</span></td><td><i class="sw ' + ["t-ec", "t-open", "t-room"][r.tier] + '"></i> ' + tierName[r.tier] + '</td><td class="n">' + fmt(r.f) + '</td><td class="n">' + fmt(p.T[r.a][r.s]) + '</td></tr>';
      }).join("") +
      unpl.map(function (u) { return '<tr><td><b>' + esc(u.id) + '</b></td><td>All</td><td colspan="2" class="err">Not placed: no open shelter within the trip limit</td><td class="n">' + fmt(u.n) + '</td><td class="n">–</td></tr>'; }).join("") +
      '</tbody></table>';
  }
  function unplacedByOrigin(p) {
    var I = p.inst, got = I.origins.map(function () { return 0; });
    p.x.forEach(function (r) { got[r.a] += r.f; });
    return I.origins.map(function (o, a) { return { id: o.id, name: o.name, n: E.demand(o, p.sc) - got[a] }; }).filter(function (u) { return u.n > 0; });
  }
  function nearDetail(p) {
    var I = p.inst;
    var h = '<table><thead><tr><th>Site</th><th>Shelters there</th><th class="n">Sent</th><th class="n">Capacity</th><th class="n">Over</th></tr></thead><tbody>';
    p.sites.slice().sort(function (a, b) { return b.load - a.load; }).forEach(function (s) {
      var names = I.shelters.filter(function (sh) { return sh.node === s.node; }).map(function (sh) { return sh.id; }).join(", ");
      h += '<tr><td><b>' + esc(s.id) + '</b></td><td>' + esc(names) + '</td><td class="n">' + fmt(s.load) + '</td><td class="n">' + fmt(s.cap) + '</td><td class="n' + (s.overflow ? ' err' : '') + '">' + fmt(s.overflow) + '</td></tr>';
    });
    h += '</tbody></table><h3>Each origin</h3><table><thead><tr><th>Origin</th><th>Goes to</th><th class="n">Persons</th><th class="n">Minutes</th></tr></thead><tbody>';
    p.choice.forEach(function (c, a) {
      if (!c) return;
      h += '<tr><td><b>' + esc(I.origins[a].id) + '</b></td><td>' + esc(I.nodes[c.node]) + '</td><td class="n">' + fmt(c.persons) + '</td><td class="n">' + fmt(c.minutes) + '</td></tr>';
    });
    return h + '</tbody></table>';
  }
  function compareKey() { return S.rev + "|" + S.ui.theta + "|plan|" + S.ui.scen + "|"; }
  function renderCompare() {
    var rules = ["lex", "time", "near"], have = {};
    rules.forEach(function (r) { var k = compareKey() + r + "|"; if (k in S.cache) have[r] = S.cache[k]; });
    var sp = scenById(S.ui.scen);
    var h = '<table><thead><tr><th>Rule</th><th class="n">Classrooms closed</th><th class="n">Learners displaced</th><th class="n">In classrooms</th><th class="n">Not placed or over</th><th class="n">Mean trip</th></tr></thead><tbody>';
    rules.forEach(function (r) {
      var p = have[r];
      if (!p) { h += '<tr><td>' + ruleName(r) + '</td><td colspan="5" class="muted">not computed yet</td></tr>'; return; }
      if (r === "near") h += '<tr><td>' + ruleName(r) + '</td><td class="n muted">not planned</td><td class="n muted">–</td><td class="n muted">–</td><td class="n">' + fmt(p.overflow) + ' over</td><td class="n">' + fmt2(p.meanTime) + '</td></tr>';
      else h += '<tr' + (r === "lex" ? ' class="sel"' : '') + '><td>' + ruleName(r) + '</td><td class="n"><b>' + fmt(p.roomsClosedTotal) + '</b></td><td class="n">' + fmt(p.learnersDisplaced) + '</td><td class="n">' + fmt(p.personsRoom) + '</td><td class="n">' + fmt(p.unplaced) + '</td><td class="n">' + fmt2(p.meanTime) + '</td></tr>';
    });
    $("compare").innerHTML = h + '</tbody></table><p class="fine" style="margin-top:.4rem">' + esc(sp.name) + ', trip limit ' + fmt(S.ui.theta) + ' min. Test network E1 (synthetic).</p>';
  }
  qa("[data-rule]").forEach(function (b) {
    b.addEventListener("click", function () { S.ui.rule = b.getAttribute("data-rule"); saveUI(); renderPlan(); });
  });
  $("compare-btn").addEventListener("click", function () {
    later(function () { ["lex", "time", "near"].forEach(function (r) { planFor(S.ui.scen, r); }); renderCompare(); });
  });
  function numInput(el, key, min) {
    el.addEventListener("change", function () {
      var v = Math.round(+el.value);
      if (!(v >= min)) { el.value = S.ui[key]; return; }
      S.ui[key] = v; saveUI(); render();
    });
  }
  numInput($("theta"), "theta", 1);
  numInput($("days"), "days", 0);

  /* ---------------------------------------------------------------- editable tables */
  var TABLES = {
    origins: { cols: [["id", "ID", "text"], ["name", "Name", "wide"], ["node", "Map point", "node"], ["zones", "Zones", "zones"], ["pop", "Population", "int"], ["vul", "Vulnerable", "int"]],
      blank: function () { return { id: nextId("O", S.data.origins), name: "New origin", node: firstNode("origin"), zones: ["PDZ"], pop: 100, vul: 20 }; } },
    shelters: { cols: [["id", "ID", "text"], ["name", "Name", "wide"], ["node", "Map point", "node"], ["kind", "Kind", "kind"], ["areaNonSchool", "Non-school m²", "num"], ["areaOpen", "School open m²", "num"], ["rooms", "Classrooms", "int"], ["learnersPerRoom", "Learners per room", "int"], ["accessible", "Accessible", "bool"], ["cap", "Capacity", "cap"]],
      blank: function () { return { id: nextId("SH", S.data.shelters), name: "New shelter", node: firstNode("town"), kind: "ec", areaNonSchool: 700, areaOpen: 0, rooms: 0, learnersPerRoom: 0, accessible: true, zones: [] }; } },
    roads: { cols: [["u", "From", "node"], ["v", "To", "node"], ["tau", "Minutes τ", "int"], ["cap", "Capacity u", "int"], ["tag", "Tag", "text"]],
      blank: function () { return { u: S.data.nodes[0] ? S.data.nodes[0].id : "", v: S.data.nodes[1] ? S.data.nodes[1].id : "", tau: 10, cap: 20, tag: "new" + (S.data.roads.length + 1) }; } },
    nodes: { cols: [["id", "ID", "text"], ["name", "Name", "wide"], ["x", "x (km)", "num"], ["y", "y (km)", "num"], ["kind", "Kind", "nodekind"]],
      blank: function () { return { id: nextId("N", S.data.nodes), name: "New point", x: 0, y: -10, kind: "town" }; } },
    candidates: { cols: [["name", "Name", "wide"], ["node", "Map point", "node"], ["area", "Floor area m²", "num"], ["cap", "Capacity", "ccap"]],
      blank: function () { return { node: firstNode("town"), name: "Ligtas Pinoy Center", area: 1050 }; } }
  };
  function nextId(prefix, list) {
    var n = list.length + 1, ids = {};
    list.forEach(function (x) { ids[x.id] = 1; });
    while (ids[prefix + n]) n++;
    return prefix + n;
  }
  function firstNode(kind) {
    var n = S.data.nodes.filter(function (x) { return x.kind === kind; })[0] || S.data.nodes[0];
    return n ? n.id : "";
  }
  function cell(tbl, i, row, col) {
    var f = col[0], t = col[2], v = row[f], a = ' data-t="' + tbl + '" data-i="' + i + '" data-f="' + f + '" aria-label="' + esc(col[1] + " of row " + (i + 1)) + '"';
    if (t === "node") return '<select' + a + '>' + S.data.nodes.map(function (n) { return '<option value="' + esc(n.id) + '"' + (n.id === v ? " selected" : "") + '>' + esc(n.id + (n.name && n.name !== n.id ? " · " + n.name : "")) + '</option>'; }).join("") + '</select>';
    if (t === "kind") return '<select' + a + '><option value="ec"' + (v !== "school" ? " selected" : "") + '>Non-school</option><option value="school"' + (v === "school" ? " selected" : "") + '>School</option></select>';
    if (t === "nodekind") return '<select' + a + '>' + ["origin", "town", "ring"].map(function (k) { return '<option' + (k === v ? " selected" : "") + '>' + k + '</option>'; }).join("") + '</select>';
    if (t === "bool") return '<input type="checkbox"' + a + (v !== false ? " checked" : "") + '>';
    if (t === "zones") return '<input type="text"' + a + ' value="' + esc((v || []).join(" ")) + '" style="min-width:7rem">';
    if (t === "int" || t === "num") {
      var bad = tbl === "origins" && f === "vul" && +row.vul > +row.pop;
      return '<input type="number" inputmode="decimal" min="0" step="' + (t === "int" ? 1 : "any") + '"' + a + ' value="' + esc(v) + '"' + (bad ? ' class="bad" title="More vulnerable residents than residents"' : "") + '>';
    }
    if (t === "cap") {
      var c = E.capFromArea(row.areaNonSchool) + (row.kind === "school" ? E.capFromArea(row.areaOpen) + 18 * (+row.rooms || 0) : 0);
      return '<span title="non-school + open space + 18 per classroom">' + fmt(c) + '</span>';
    }
    if (t === "ccap") return fmt(E.capFromArea(row.area));
    return '<input type="text"' + a + ' value="' + esc(v) + '"' + (t === "wide" ? ' class="wide"' : "") + '>';
  }
  function renderTable(tbl) {
    var el = $("tbl-" + tbl);
    if (!el) return;
    var def = TABLES[tbl], list = tbl === "candidates" ? S.data.candidates : S.data[tbl];
    var h = '<table><thead><tr>' + def.cols.map(function (c) { return '<th' + (c[2] === "int" || c[2] === "num" || c[2] === "cap" || c[2] === "ccap" ? ' class="n"' : '') + '>' + esc(c[1]) + '</th>'; }).join("") + '<th><span class="sr-only">Delete</span></th></tr></thead><tbody>';
    list.forEach(function (row, i) {
      h += '<tr>' + def.cols.map(function (c) { return '<td' + (c[2] === "cap" || c[2] === "ccap" ? ' class="n"' : '') + '>' + cell(tbl, i, row, c) + '</td>'; }).join("") +
        '<td><button type="button" class="del" data-del="' + tbl + '" data-i="' + i + '" aria-label="Delete row ' + (i + 1) + '"><svg aria-hidden="true"><use href="#i-x"/></svg></button></td></tr>';
    });
    el.innerHTML = h + '</tbody></table>' + (list.length ? "" : '<p class="muted small">No rows.</p>');
  }
  function renderTables() { Object.keys(TABLES).forEach(renderTable); }
  document.addEventListener("change", function (e) {
    var el = e.target, tbl = el.getAttribute && el.getAttribute("data-t");
    if (!tbl) return;
    var list = tbl === "candidates" ? S.data.candidates : S.data[tbl], i = +el.getAttribute("data-i"), f = el.getAttribute("data-f");
    var row = list[i], col = TABLES[tbl].cols.filter(function (c) { return c[0] === f; })[0];
    if (!row || !col) return;
    var t = col[2];
    if (t === "int" || t === "num") {
      var v = +el.value;
      if (!isFinite(v) || (v < 0 && !(tbl === "nodes"))) { toast("Enter a number of zero or more."); el.value = row[f]; return; }
      if (f === "tau") v = Math.max(1, Math.round(v));
      else if (t === "int") v = Math.round(v);
      row[f] = v;
    } else if (t === "bool") row[f] = !!el.checked;
    else if (t === "zones") row[f] = el.value.split(/[\s,;]+/).filter(Boolean);
    else if (f === "id") {
      var nv = el.value.trim();
      if (!nv || list.some(function (r, j) { return j !== i && r.id === nv; })) { toast("IDs must be unique and not empty."); el.value = row[f]; return; }
      if (tbl === "nodes") renameNode(row.id, nv);
      row[f] = nv;
    } else row[f] = el.value;
    if (tbl === "shelters" && f === "kind" && row.kind !== "school") { row.areaOpen = 0; row.rooms = 0; row.learnersPerRoom = 0; }
    saveData();
    renderTable(tbl);
    if (tbl === "nodes") { renderTables(); fillOrigins(); }
    if (tbl === "origins") fillOrigins();
    render();
  });
  function renameNode(from, to) {
    S.data.roads.forEach(function (r) { if (r.u === from) r.u = to; if (r.v === from) r.v = to; });
    S.data.origins.forEach(function (o) { if (o.node === from) o.node = to; });
    S.data.shelters.forEach(function (s) { if (s.node === from) s.node = to; });
    S.data.candidates.forEach(function (c) { if (c.node === from) c.node = to; });
  }
  document.addEventListener("click", function (e) {
    var t = e.target.closest ? e.target.closest("[data-add],[data-del]") : null;
    if (!t) return;
    var add = t.getAttribute("data-add"), del = t.getAttribute("data-del");
    if (add) {
      var list = add === "candidates" ? S.data.candidates : S.data[add];
      list.push(TABLES[add].blank());
      saveData(); renderTable(add); if (add === "origins") fillOrigins(); render();
      toast("Row added. Edit it in the table.");
    } else if (del) {
      var l2 = del === "candidates" ? S.data.candidates : S.data[del], i = +t.getAttribute("data-i"), row = l2[i];
      if (del === "nodes" && row) {
        var used = S.data.roads.some(function (r) { return r.u === row.id || r.v === row.id; }) || S.data.origins.some(function (o) { return o.node === row.id; }) || S.data.shelters.some(function (s) { return s.node === row.id; });
        if (used) { toast("This map point is used by a road, origin or shelter. Remove those first."); return; }
      }
      l2.splice(i, 1);
      saveData(); renderTable(del); if (del === "origins") fillOrigins(); render();
    }
  });

  /* ---------------------------------------------------------------- CLEARANCE */
  function bridgesAll() {
    var out = [];
    (S.data.channels || []).forEach(function (c) { (c.bridges || []).forEach(function (b) { out.push({ tag: b, ch: c.id }); }); });
    return out;
  }
  function renderClear() {
    qa(".scen-seg").forEach(function (el) { drawSeg(el, S.ui.scen, function (id) { S.ui.scen = id; S.ui.extra = []; saveUI(); render(); }); });
    var sp = scenById(S.ui.scen), locked = {};
    (sp.closed || []).forEach(function (t) { locked[t] = true; });
    S.ui.extra = (S.ui.extra || []).filter(function (t) { return !locked[t]; });
    var extraSet = {};
    S.ui.extra.forEach(function (t) { extraSet[t] = true; });
    $("bridge-chips").innerHTML = bridgesAll().map(function (b) {
      var closed = locked[b.tag] || extraSet[b.tag];
      return '<button type="button" class="chip" data-bridge-chip="' + esc(b.tag) + '" aria-pressed="' + (closed ? "true" : "false") + '"' + (locked[b.tag] ? ' disabled title="Closed by the scenario"' : "") + '><i class="bx"></i>' + esc(b.tag) + (locked[b.tag] ? " (scenario)" : "") + '</button>';
    }).join("") || '<p class="muted small">This network has no bridges on lahar channels.</p>';
    qa("[data-bridge-chip]").forEach(function (b) { b.onclick = function () { toggleBridge(b.getAttribute("data-bridge-chip")); }; });
    var out = $("clear-result"), cr = $("closure-result");
    out.classList.add("computing");
    later(function () {
      var p = planFor(S.ui.scen, "lex");
      out.classList.remove("computing");
      var sup = p.supplies, curve0 = clearanceCurve(p, p.sc, p.clearance);
      var h = '<div class="kpis" style="grid-template-columns:repeat(3,minmax(0,1fr))">' +
        '<div class="kpi good"><b>' + (p.clearance === Infinity ? "∞" : fmt(p.clearance)) + '</b><span>clearance time T* (min)</span></div>' +
        '<div class="kpi"><b>' + fmt(p.clearanceLB) + '</b><span>lower bound (min)</span></div>' +
        '<div class="kpi"><b>' + fmt(p.clearanceCalls) + '</b><span>maximum flows solved (doubling, bisection)</span></div></div>';
      h += '<p class="small muted">' + fmt(p.placed) + ' evacuees of the school-preserving plan, ' + esc(sp.name) + '. Exact: the smallest T with F(T) = ' + fmt(p.placed) + ' on the time-expanded network.</p>';
      var res = null;
      if (S.ui.extra.length) res = closureResult(p, sp);
      h += chartSVG(curve0, res && res.curve, p.placed, p.clearance, p.clearanceLB, res ? res.fixed : null);
      out.innerHTML = h;
      cr.innerHTML = res ? res.html : '<p class="note">All bridges ' + ((sp.closed || []).length ? "outside the scenario's closures " : "") + 'are open. Close one to see its effect.</p>';
      M.draw($("map-clear"), S.data, { scenario: sp, extraClosed: S.ui.extra, flows: flowsOf(res ? res.fresh : p), bridgesClickable: true, label: mapLabel("Clearance,", sp) });
      void sup;
      renderStudy(sp);
    });
  }
  function clearanceCurve(p, sc, T) {
    if (!p.supplies || !p.placed) return [];
    var until = (T === Infinity || T == null ? 120 : T) + 10;
    return E.arrivalCurve(p.inst, sc, p.supplies.sup, p.supplies.caps, until, 2);
  }
  function closureResult(p, sp) {
    var spec = { id: sp.id, zones: sp.zones, closed: (sp.closed || []).concat(S.ui.extra) };
    var sc2 = E.scenario(spec);
    var fixed = cached("fixed|" + sp.id + "|" + S.ui.extra.slice().sort().join(","), function () { return E.clearanceTime(p.inst, sc2, p.supplies.sup, p.supplies.caps).T; });
    var fresh = planFor(S.ui.scen, "lex", S.ui.extra);
    var curve = fixed === Infinity ? null : E.arrivalCurve(p.inst, sc2, p.supplies.sup, p.supplies.caps, fixed + 10, 2);
    var delta = fixed === Infinity ? Infinity : fixed - p.clearance;
    var trapped = unplacedByOrigin(fresh);
    var h = '<div class="kpis" style="grid-template-columns:repeat(3,minmax(0,1fr))">' +
      '<div class="kpi bad"><b>' + (fixed === Infinity ? "∞" : fmt(fixed)) + '</b><span>clearance, same plan (min)</span></div>' +
      '<div class="kpi bad"><b>' + (delta === Infinity ? "∞" : (delta > 0 ? "+" : "") + fmt(delta)) + '</b><span>change Δ (min)</span></div>' +
      '<div class="kpi ' + (fresh.unplaced ? "bad" : "good") + '"><b>' + fmt(fresh.unplaced) + '</b><span>trapped: no shelter reachable</span></div></div>';
    if (fixed === Infinity) h += '<p class="note warn">With the plan held fixed, some evacuees can no longer reach the shelter the plan gave them at all.</p>';
    h += '<p class="small">A fresh plan for the damaged network places ' + fmt(fresh.placed) + ' of ' + fmt(fresh.demand) + ' evacuees, closes ' + fmt(fresh.roomsClosedTotal) + ' classrooms, and clears in ' + minutes(fresh.clearance) + '.</p>';
    if (trapped.length) h += '<p class="note warn"><b>Cut off:</b> ' + trapped.map(function (u) { return esc(u.id) + " (" + fmt(u.n) + " residents)"; }).join(", ") + '. No open road leads to a shelter with room within the trip limit.</p>';
    return { html: h, fixed: fixed, curve: curve, fresh: fresh };
  }
  function toggleBridge(tag) {
    var i = S.ui.extra.indexOf(tag);
    if (i >= 0) S.ui.extra.splice(i, 1); else S.ui.extra.push(tag);
    saveUI(); renderClear();
  }
  $("map-clear").addEventListener("click", function (e) {
    var g = e.target.closest ? e.target.closest("[data-bridge]") : null;
    if (g) toggleBridge(g.getAttribute("data-bridge"));
  });
  $("map-clear").addEventListener("keydown", function (e) {
    if (e.key !== "Enter" && e.key !== " ") return;
    var g = e.target.closest ? e.target.closest("[data-bridge]") : null;
    if (g) { e.preventDefault(); var tag = g.getAttribute("data-bridge"); toggleBridge(tag); var again = $("map-clear").querySelector('[data-bridge="' + tag + '"]'); if (again) again.focus(); }
  });
  qa("[data-close]").forEach(function (b) {
    b.addEventListener("click", function () {
      var w = b.getAttribute("data-close"), sp = scenById(S.ui.scen), locked = {};
      (sp.closed || []).forEach(function (t) { locked[t] = true; });
      var pick = bridgesAll().filter(function (x) { return (w === "AB" || x.ch === w) && !locked[x.tag]; }).map(function (x) { return x.tag; });
      S.ui.extra = w === "none" ? [] : pick;
      saveUI(); renderClear();
    });
  });
  function renderStudy(sp) {
    var el = $("study");
    var groups = [{ name: "No bridge closed", tags: [] }];
    (S.data.channels || []).forEach(function (c) { groups.push({ name: "Channel " + c.id + " cut (" + c.bridges.join(", ") + ")", tags: c.bridges.slice() }); });
    if ((S.data.channels || []).length > 1) groups.push({ name: "Every channel cut", tags: bridgesAll().map(function (b) { return b.tag; }) });
    $("study-pill").textContent = "zones " + sp.zones.join(", ");
    var rows = cached("study|" + sp.zones.join(","), function () {
      return E.closureStudy(Object.assign({}, S.data, { thetaMax: S.ui.theta }), { id: sp.id, zones: sp.zones, closed: [] }, groups, { thetaMax: S.ui.theta });
    });
    el.innerHTML = '<table><thead><tr><th>Closure</th><th class="n">Clearance, same plan</th><th class="n">Change Δ</th><th class="n">Trapped</th><th class="n">In classrooms</th><th class="n">Classrooms closed</th><th class="n">Clearance, new plan</th><th class="n">Mean trip</th></tr></thead><tbody>' +
      rows.map(function (r) {
        return '<tr><td>' + esc(r.name) + '</td><td class="n">' + minutes(r.clearanceFixedPlan) + '</td><td class="n">' + (r.delta === Infinity || r.delta == null || isNaN(r.delta) ? "∞" : (r.delta > 0 ? "+" : "") + fmt(r.delta)) + '</td><td class="n' + (r.unplaced ? " err" : "") + '">' + fmt(r.unplaced) + '</td><td class="n">' + fmt(r.personsRoom) + '</td><td class="n">' + fmt(r.roomsClosed) + '</td><td class="n">' + minutes(r.clearanceNewPlan) + '</td><td class="n">' + fmt2(r.meanTime) + '</td></tr>';
      }).join("") + '</tbody></table>';
  }
  function chartSVG(c1, c2, goal, T, LB, T2) {
    if (!c1 || !c1.length) return "";
    var W = 560, H = 230, L = 46, R = 14, Tp = 14, B = 34;
    var xmax = Math.max(c1[c1.length - 1][0], c2 && c2.length ? c2[c2.length - 1][0] : 0, 10);
    var ymax = Math.max(goal, 1);
    var X = function (t) { return L + (W - L - R) * t / xmax; }, Y = function (v) { return H - B - (H - B - Tp) * v / ymax; };
    var path = function (c) { return c.map(function (q, i) { return (i ? "L" : "M") + X(q[0]).toFixed(1) + " " + Y(q[1]).toFixed(1); }).join(""); };
    var h = '<svg class="chart" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="Evacuees inside shelters by minute. Everyone in by minute ' + (T === Infinity ? "never" : T) + (T2 != null ? (T2 === Infinity ? "; with the closure, never" : "; with the closure, minute " + T2) : "") + '.">';
    var step = xmax > 150 ? 50 : xmax > 60 ? 20 : 10;
    for (var t = 0; t <= xmax; t += step) h += '<line class="grid" x1="' + X(t) + '" x2="' + X(t) + '" y1="' + Tp + '" y2="' + (H - B) + '"/><text x="' + X(t) + '" y="' + (H - B + 16) + '" text-anchor="middle">' + t + '</text>';
    [0, 0.5, 1].forEach(function (f) { var v = Math.round(ymax * f); h += '<text x="' + (L - 6) + '" y="' + (Y(v) + 4) + '" text-anchor="end">' + fmt(v) + '</text>'; });
    h += '<line class="ax" x1="' + L + '" x2="' + (W - R) + '" y1="' + (H - B) + '" y2="' + (H - B) + '"/>';
    h += '<line class="goal" x1="' + L + '" x2="' + (W - R) + '" y1="' + Y(goal) + '" y2="' + Y(goal) + '"/>';
    h += '<text x="' + (W / 2) + '" y="' + (H - 3) + '" text-anchor="middle">minutes after the order</text>';
    if (LB != null && isFinite(LB)) h += '<line class="lb" x1="' + X(LB) + '" x2="' + X(LB) + '" y1="' + Tp + '" y2="' + (H - B) + '"/><text class="lab g" x="' + (X(LB) - 4) + '" y="' + (Tp + 30) + '" text-anchor="end">bound ' + LB + '</text>';
    h += '<path class="s1" d="' + path(c1) + '"/>';
    if (isFinite(T)) h += '<line class="mk" x1="' + X(T) + '" x2="' + X(T) + '" y1="' + Tp + '" y2="' + (H - B) + '"/><text class="lab t" x="' + (X(T) + 4) + '" y="' + (Tp + 12) + '">T* ' + T + '</text>';
    if (c2 && c2.length) {
      h += '<path class="s2" d="' + path(c2) + '"/>';
      if (T2 != null && isFinite(T2)) h += '<line class="mk2" x1="' + X(T2) + '" x2="' + X(T2) + '" y1="' + Tp + '" y2="' + (H - B) + '"/><text class="lab r" x="' + (X(T2) + 4) + '" y="' + (Tp + 26) + '">closed ' + T2 + '</text>';
    }
    return h + '</svg>';
  }

  /* ---------------------------------------------------------------- SITING */
  function renderSite() {
    drawSeg($("site-scen"), S.ui.siteScen, function (id) { S.ui.siteScen = id; S.ui.siteRow = null; saveUI(); renderSite(); });
    $("site-theta").value = S.ui.siteTheta;
    $("site-k").value = S.ui.siteK;
    renderTable("candidates");
    var key = siteKey(), res = S.cache[key];
    var sp = scenById(S.ui.siteScen);
    if (!res) {
      $("site-result").innerHTML = '<h2>Results</h2><p class="muted small">Press Choose sites to run the greedy choice, check it against every possible set, and recompute the plan with the new centers.</p>';
      M.draw($("map-site"), S.data, { scenario: sp, candidates: S.data.candidates.map(function (c) { return { node: c.node, title: c.name + ", " + fmt(E.capFromArea(c.area)) + " persons" }; }), label: mapLabel("Candidate sites,", sp) });
      return;
    }
    var rows = res.rows, sel = S.ui.siteRow != null && rows[S.ui.siteRow] ? S.ui.siteRow : rows.length - 1;
    var h = '<div class="res-title"><h2>Greedy choice</h2><span class="pill">' + esc(sp.name) + '</span><span class="pill gold">θ = ' + fmt(res.theta) + ' min</span></div>';
    h += '<p class="small muted" style="margin:.3rem 0 .5rem">Coverage now: ' + fmt(res.phi0) + ' evacuees can be sheltered outside classrooms within ' + fmt(res.theta) + ' minutes.</p>';
    h += '<div class="tbl-wrap"><table><thead><tr><th>k</th><th>Greedy sites</th><th class="n">Gain f(S)</th><th class="n">Best gain</th><th class="n">Greedy / best</th><th class="n">Guarantee</th></tr></thead><tbody>';
    rows.forEach(function (r, i) {
      var ratio = r.bestGain ? r.gain / r.bestGain : 1, g = 1 - Math.pow(1 - 1 / r.k, r.k);
      h += '<tr' + (i === sel ? ' class="sel"' : '') + ' data-site-row="' + i + '" style="cursor:pointer"><td>' + r.k + '</td><td><b>' + esc(r.sites.join(", ")) + '</b></td><td class="n">' + fmt(r.gain) + '</td><td class="n">' + (r.bestGain == null ? "–" : fmt(r.bestGain)) + '</td><td class="n">' + (r.bestGain == null ? "–" : (100 * ratio).toFixed(1) + "%") + '</td><td class="n">≥ ' + (100 * g).toFixed(1) + '%</td></tr>';
    });
    h += '</tbody></table></div>';
    h += '<h3>Plan with the new centers</h3><div class="tbl-wrap"><table><thead><tr><th>k</th><th class="n">Not placed</th><th class="n">In classrooms</th><th class="n">Classrooms closed</th><th class="n">Learners displaced</th><th class="n">Clearance</th></tr></thead><tbody>';
    h += '<tr><td>0</td><td class="n">' + fmt(res.base.unplaced) + '</td><td class="n">' + fmt(res.base.personsRoom) + '</td><td class="n">' + fmt(res.base.roomsClosedTotal) + '</td><td class="n">' + fmt(res.base.learnersDisplaced) + '</td><td class="n">' + minutes(res.base.clearance) + '</td></tr>';
    rows.forEach(function (r, i) {
      h += '<tr' + (i === sel ? ' class="sel"' : '') + ' data-site-row="' + i + '" style="cursor:pointer"><td>' + r.k + '</td><td class="n">' + fmt(r.unplaced) + '</td><td class="n">' + fmt(r.personsRoom) + '</td><td class="n">' + fmt(r.roomsClosed) + '</td><td class="n">' + fmt(r.learners) + '</td><td class="n">' + minutes(r.clearance) + '</td></tr>';
    });
    h += '</tbody></table></div>';
    var gains = res.singleGains, ids = Object.keys(gains), gmax = Math.max.apply(null, ids.map(function (k) { return gains[k]; }).concat([1]));
    h += '<h3>Gain of each site alone</h3><div class="bars">' + ids.map(function (k) {
      var top = rows[0] && rows[0].sites[0] === k;
      return '<div><span>' + esc(k) + '</span><i class="' + (top ? "top" : "") + '" style="width:' + (100 * gains[k] / gmax).toFixed(1) + '%"></i><em>' + fmt(gains[k]) + '</em></div>';
    }).join("") + '</div>';
    h += '<p class="note">The gain is monotone and submodular (Proposition 10), so greedy reaches at least 1 − (1 − 1/k)<sup>k</sup> ≥ 63.2% of the best set (Nemhauser et al., 1978). Here it is checked against every set of k sites.</p>';
    $("site-result").innerHTML = h;
    qa("[data-site-row]").forEach(function (tr) { tr.onclick = function () { S.ui.siteRow = +tr.getAttribute("data-site-row"); saveUI(); renderSite(); }; });
    var row = rows[sel], chosen = {};
    row.sites.forEach(function (s, i) { chosen[s] = i + 1; });
    var extra = row.sites.map(function (id) {
      var c = S.data.candidates.filter(function (x) { return x.node === id; })[0];
      return { id: "LPC-" + id, name: c ? c.name : "Ligtas Pinoy Center", node: id, kind: "ec", areaNonSchool: c ? c.area : 0, areaOpen: 0, rooms: 0, learnersPerRoom: 0, accessible: true, zones: [] };
    });
    var I2 = E.makeInstance(S.data, { extraShelters: extra, thetaMax: S.ui.theta }), sc = E.scenario(sp);
    var p2 = cached("siteplan|" + key + "|" + sel, function () { var p = E.plan(I2, sc, "lex"); p.inst = I2; p.sc = sc; p.rule = "lex"; return p; });
    var data2 = Object.assign({}, S.data, { shelters: S.data.shelters.concat(extra) });
    M.draw($("map-site"), data2, {
      scenario: sp, flows: flowsOf(p2), siteNotes: siteNotesOf(p2),
      candidates: S.data.candidates.map(function (c) { var r = chosen[c.node]; return { node: c.node, chosen: !!r, label: r ? "#" + r : "", title: c.name + ", " + fmt(E.capFromArea(c.area)) + " persons" + (r ? ", chosen #" + r : "") }; }),
      label: mapLabel("Sites chosen,", sp)
    });
  }
  function siteKey() { return S.rev + "|" + S.ui.theta + "|site|" + S.ui.siteScen + "|" + S.ui.siteTheta + "|" + S.ui.siteK; }
  $("site-run").addEventListener("click", function () {
    var b = $("site-run");
    b.disabled = true; $("site-result").classList.add("computing");
    later(function () {
      var t0 = Date.now(), sp = scenById(S.ui.siteScen);
      var cands = S.data.candidates.filter(function (c) { return S.data.nodes.some(function (n) { return n.id === c.node; }); });
      var k = Math.max(1, Math.min(S.ui.siteK, cands.length));
      if (!cands.length) { toast("Add at least one candidate site."); b.disabled = false; $("site-result").classList.remove("computing"); return; }
      var res = E.siting(S.data, sp, S.ui.siteTheta, cands, k, { thetaMax: S.ui.theta });
      res.base = E.evaluate(inst(), E.scenario(sp), "lex");
      S.cache[siteKey()] = res;
      S.ui.siteRow = null;
      $("site-time").textContent = "Computed in " + (Date.now() - t0) + " ms.";
      b.disabled = false; $("site-result").classList.remove("computing");
      renderSite();
    });
  });
  numInputSite($("site-theta"), "siteTheta", 1);
  numInputSite($("site-k"), "siteK", 1);
  function numInputSite(el, key, min) {
    el.addEventListener("change", function () {
      var v = Math.round(+el.value);
      if (!(v >= min)) { el.value = S.ui[key]; return; }
      if (key === "siteK") v = Math.min(v, 8);
      S.ui[key] = v; S.ui.siteRow = null; saveUI(); renderSite();
    });
  }

  /* ---------------------------------------------------------------- RESIDENT */
  function fillOrigins() {
    var sel = $("res-origin");
    if (!S.data.origins.some(function (o) { return o.id === S.ui.resOrigin; })) S.ui.resOrigin = S.data.origins[0] ? S.data.origins[0].id : null;
    sel.innerHTML = S.data.origins.map(function (o) { return '<option value="' + esc(o.id) + '"' + (o.id === S.ui.resOrigin ? " selected" : "") + '>' + esc(o.name || o.id) + '</option>'; }).join("");
  }
  $("res-origin").addEventListener("change", function () { S.ui.resOrigin = this.value; saveUI(); renderRes(); });
  $("res-vul").addEventListener("change", function () { S.ui.resVul = this.checked; saveUI(); renderRes(); });
  $("map-res").addEventListener("click", function (e) {
    var g = e.target.closest ? e.target.closest("[data-origin]") : null;
    if (g) { S.ui.resOrigin = g.getAttribute("data-origin"); saveUI(); fillOrigins(); renderRes(); }
  });
  $("map-res").addEventListener("keydown", function (e) {
    if (e.key !== "Enter" && e.key !== " ") return;
    var g = e.target.closest ? e.target.closest("[data-origin]") : null;
    if (g) { e.preventDefault(); S.ui.resOrigin = g.getAttribute("data-origin"); saveUI(); fillOrigins(); renderRes(); }
  });
  function renderRes() {
    $("res-vul").checked = !!S.ui.resVul;
    var box = $("res-cards");
    var oi = -1;
    S.data.origins.forEach(function (o, i) { if (o.id === S.ui.resOrigin) oi = i; });
    if (oi < 0) { box.innerHTML = '<p class="muted">Add an origin in the Planner first.</p>'; M.draw($("map-res"), S.data, { scenario: scenById(S.ui.resScen), originsClickable: true }); return; }
    box.classList.add("computing");
    later(function () {
      box.classList.remove("computing");
      var html = "", route = null, focusScen = scenById(S.ui.resScen);
      (S.data.scenarios || []).forEach(function (sp) {
        var p = planFor(sp.id, "lex"), I = p.inst;
        var a = -1;
        I.origins.forEach(function (o, i) { if (o.id === S.ui.resOrigin) a = i; });
        var o = I.origins[a];
        var sel = sp.id === S.ui.resScen;
        var h = '<div class="rc' + (sel ? " sel" : "") + '" data-res-scen="' + esc(sp.id) + '"><h3>' + esc(sp.name) + ' ';
        if (!o || E.demand(o, p.sc) === 0) {
          html += h + '<span class="pill teal">No evacuation for your area</span></h3><p class="small muted">Your area is outside the active hazard zones in this scenario. Stay alert for announcements.</p></div>';
          return;
        }
        var want = S.ui.resVul ? "V" : "N";
        var rows = {}, total = 0;
        p.x.forEach(function (r) {
          if (r.a !== a) return;
          if (r.cls !== want && !(want === "N" && o.vul === o.pop)) return;
          var sl = p.slots[r.k], k = sl.s + "|" + sl.tier;
          if (!rows[k]) rows[k] = { s: sl.s, tier: sl.tier, f: 0 };
          rows[k].f += r.f; total += r.f;
        });
        var groupSize = want === "V" ? E.vulnerable(o, p.sc) : E.demand(o, p.sc) - E.vulnerable(o, p.sc);
        var list = Object.keys(rows).map(function (k) { return rows[k]; }).sort(function (x, y) { return y.f - x.f; });
        h += '<span class="pill red">Evacuate</span></h3>';
        if (!list.length) {
          html += h + '<p class="note warn">No shelter place is planned for this group within the trip limit. Ask your barangay officials.</p></div>';
          return;
        }
        if (sel) { var r0 = E.route(I, p.sc, o.node, I.shelters[list[0].s].node); route = r0.path; }
        var tierName = ["non-school space", "school open space", "classroom"];
        h += '<div class="dest">' + list.map(function (r) {
          var sh = I.shelters[r.s], town = nodeName(I.nodes[sh.node]);
          return '<div><span class="big">' + fmt(p.T[a][r.s]) + '<small>min</small></span><b>' + esc(sh.name) + ' (' + esc(sh.id) + ')</b><p>' + esc(town) + ' · ' + tierName[r.tier] + ' · ' + (sh.accessible ? "accessible" : "not accessible (stairs)") + ' · ' + fmt(r.f) + ' of ' + fmt(groupSize) + ' ' + (want === "V" ? "vulnerable residents" : "residents") + '</p></div>';
        }).join("") + '</div>';
        if (list.length > 1) h += '<p class="small muted" style="margin-top:.4rem">Your barangay is split between ' + list.length + ' places. Officials say which group you are in.</p>';
        if (total < groupSize) h += '<p class="note warn">' + fmt(groupSize - total) + ' in this group have no planned place within the trip limit.</p>';
        html += h + '</div>';
      });
      box.innerHTML = html;
      qa("[data-res-scen]").forEach(function (c) { c.onclick = function () { S.ui.resScen = c.getAttribute("data-res-scen"); saveUI(); renderRes(); }; });
      M.draw($("map-res"), S.data, { scenario: focusScen, route: route, selectOrigin: S.ui.resOrigin, originsClickable: true, label: mapLabel("Your route,", focusScen) });
    });
  }
  function nodeName(id) { var n = S.data.nodes.filter(function (x) { return x.id === id; })[0]; return n ? (n.name || n.id) : id; }

  /* ---------------------------------------------------------------- CAPACITY */
  function renderCap() {
    var A = Math.max(0, +$("cap-area").value || 0);
    $("cap-area-out").textContent = fmt(E.capFromArea(A));
    $("cap-area-f").textContent = "⌊" + A + " ÷ 3.5⌋ = " + fmt(E.capFromArea(A));
    var n = Math.max(0, Math.round(+$("cap-rooms").value || 0)), len = Math.max(0, +$("cap-len").value || 0), wid = Math.max(0, +$("cap-wid").value || 0);
    var per = E.capFromArea(len * wid);
    $("cap-rooms-out").textContent = fmt(n * per);
    $("cap-rooms-sub").textContent = "evacuees, " + per + " per classroom of " + (Math.round(len * wid * 10) / 10) + " m²";
    $("cap-rooms-f").textContent = n + " × ⌊" + (Math.round(len * wid * 10) / 10) + " ÷ 3.5⌋ = " + n + " × " + per + " = " + fmt(n * per);
    var ev = Math.max(0, Math.round(+$("cap-ev").value || 0)), lpr = Math.max(0, Math.round(+$("cap-lpr").value || 0)), d = Math.max(0, Math.round(+$("cap-days").value || 0));
    var K = Math.ceil(ev / 18);
    $("cap-ev-out").textContent = fmt(K);
    $("cap-ev-sub").textContent = "classrooms closed, " + fmt(K * lpr) + " learners displaced, " + fmt(K * d) + " classroom-days";
    $("cap-ev-f").textContent = "K = ⌈" + ev + " ÷ 18⌉ = " + K + "; L = " + K + " × " + lpr + " = " + fmt(K * lpr) + "; " + K + " × " + d + " days = " + fmt(K * d);
  }
  ["cap-area", "cap-rooms", "cap-len", "cap-wid", "cap-ev", "cap-lpr", "cap-days"].forEach(function (id) { $(id).addEventListener("input", renderCap); });

  /* ---------------------------------------------------------------- DATA: export / import */
  function download(name, text, type) {
    var blob = new Blob([text], { type: type });
    var url = URL.createObjectURL(blob), a = document.createElement("a");
    a.href = url; a.download = name; document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(url); a.remove(); }, 1000);
  }
  var CSV = {
    origins: ["id", "name", "node", "zones", "pop", "vul"],
    shelters: ["id", "name", "node", "kind", "areaNonSchool", "areaOpen", "rooms", "learnersPerRoom", "accessible", "zones"],
    roads: ["u", "v", "tau", "cap", "tag"],
    nodes: ["id", "name", "x", "y", "kind"]
  };
  function csvCell(v) {
    var s = Array.isArray(v) ? v.join(" ") : v === true ? "yes" : v === false ? "no" : String(v == null ? "" : v);
    return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }
  function toCSV(tbl) {
    var cols = CSV[tbl];
    return [cols.join(",")].concat(S.data[tbl].map(function (r) { return cols.map(function (c) { return csvCell(r[c]); }).join(","); })).join("\r\n") + "\r\n";
  }
  function parseCSV(text) {
    var rows = [], row = [], cur = "", q = false, i = 0;
    text = text.replace(/^﻿/, "");
    for (; i < text.length; i++) {
      var ch = text[i];
      if (q) {
        if (ch === '"') { if (text[i + 1] === '"') { cur += '"'; i++; } else q = false; }
        else cur += ch;
      } else if (ch === '"') q = true;
      else if (ch === ",") { row.push(cur); cur = ""; }
      else if (ch === "\n" || ch === "\r") { if (ch === "\r" && text[i + 1] === "\n") i++; row.push(cur); cur = ""; if (row.some(function (c) { return c !== ""; })) rows.push(row); row = []; }
      else cur += ch;
    }
    row.push(cur);
    if (row.some(function (c) { return c !== ""; })) rows.push(row);
    return rows;
  }
  function fromCSV(text) {
    var rows = parseCSV(text);
    if (rows.length < 1) throw new Error("The file is empty.");
    var head = rows[0].map(function (h) { return h.trim(); });
    var tbl = null;
    Object.keys(CSV).forEach(function (k) { if (!tbl && CSV[k].every(function (c) { return head.indexOf(c) >= 0 || c === "name" || c === "zones" || c === "kind" || c === "accessible" || c === "tag"; })) tbl = k; });
    if (head.indexOf("pop") >= 0) tbl = "origins";
    else if (head.indexOf("rooms") >= 0 || head.indexOf("areaNonSchool") >= 0) tbl = "shelters";
    else if (head.indexOf("tau") >= 0) tbl = "roads";
    else if (head.indexOf("x") >= 0 && head.indexOf("y") >= 0) tbl = "nodes";
    if (!tbl) throw new Error("Unknown table. The header must match one of the tables listed below the buttons.");
    var NUM = { pop: 1, vul: 1, areaNonSchool: 1, areaOpen: 1, rooms: 1, learnersPerRoom: 1, tau: 1, cap: 1, x: 1, y: 1 };
    var list = rows.slice(1).map(function (r, ri) {
      var o = {};
      head.forEach(function (h, j) {
        var v = (r[j] == null ? "" : r[j]).trim();
        if (NUM[h]) { var n = +v; if (!isFinite(n) || v === "") throw new Error("Row " + (ri + 2) + ": " + h + " must be a number."); o[h] = n; }
        else if (h === "zones") o[h] = v.split(/[\s;]+/).filter(Boolean);
        else if (h === "accessible") o[h] = !/^(no|false|0|n)$/i.test(v);
        else o[h] = v;
      });
      if (tbl === "shelters" && !o.kind) o.kind = (o.rooms > 0 || o.areaOpen > 0) ? "school" : "ec";
      if (tbl === "shelters" && !o.zones) o.zones = [];
      if (tbl === "roads" && !o.tag) o.tag = "r" + (ri + 1);
      return o;
    });
    return { tbl: tbl, list: list };
  }
  $("exp-json").addEventListener("click", function () { download("ligta-s-data.json", JSON.stringify(S.data, null, 1), "application/json"); });
  qa("[data-csv]").forEach(function (b) { b.addEventListener("click", function () { var t = b.getAttribute("data-csv"); download("ligta-s-" + t + ".csv", toCSV(t), "text/csv"); }); });
  $("imp-file").addEventListener("change", function () {
    var file = this.files && this.files[0], input = this;
    if (!file) return;
    var rd = new FileReader();
    rd.onload = function () {
      try {
        var text = String(rd.result);
        if (/\.json$/i.test(file.name) || /^\s*\{/.test(text)) {
          var d = JSON.parse(text);
          if (!validData(d)) throw new Error("This JSON has no nodes, roads, origins and shelters.");
          S.data = normalize(d);
          toast("Imported " + file.name + ".");
        } else {
          var r = fromCSV(text);
          S.data[r.tbl] = r.list;
          toast("Imported " + r.list.length + " " + r.tbl + " from " + file.name + ".");
        }
        S.ui.extra = []; saveUI();
        saveData(); renderTables(); fillOrigins(); render();
      } catch (e) { toast("Could not import: " + e.message); }
      input.value = "";
    };
    rd.readAsText(file);
  });
  $("reset-data").addEventListener("click", function () {
    if (!confirm("Replace your data with the demo test network E1? Your edits in this browser will be lost.")) return;
    S.data = clone(DEMO); S.edited = false; S.rev++; S.cache = {};
    S.ui.theta = S.data.thetaMax; S.ui.extra = [];
    drop(KEY_DATA); saveUI();
    setSaveStatus("Demo data restored.");
    banner(); renderTables(); fillOrigins(); render();
  });

  /* ---------------------------------------------------------------- render */
  function render() {
    var t = S.ui.tab;
    if (t === "plan") renderPlan();
    else if (t === "clear") renderClear();
    else if (t === "site") renderSite();
    else if (t === "res") renderRes();
    else if (t === "cap") renderCap();
    else if (t === "data") renderTables();
  }
  var resizeT = null;
  window.addEventListener("resize", function () { clearTimeout(resizeT); resizeT = setTimeout(function () { qa(".seg").forEach(function () {}); render(); }, 250); });

  applyTheme();
  banner();
  renderTables();
  fillOrigins();
  renderCap();
  setSaveStatus(storageOK ? (S.edited ? "Your edited data is loaded from this browser." : "Showing the demo network. Edits are saved in this browser.") : "Saving is unavailable in this browser. Export to keep your edits.");
  var h0 = location.hash.slice(1);
  showTab(TABS.indexOf(h0) >= 0 ? h0 : S.ui.tab);
  void busy;

  /* offline copy when installed from the website */
  if ("serviceWorker" in navigator && window.isSecureContext && location.protocol !== "file:" && document.querySelector('link[rel="manifest"]')) {
    window.addEventListener("load", function () { navigator.serviceWorker.register("../sw.js", { scope: "../" }).catch(function () {}); });
  }
})();
