/* LIGTA-S website: theme switch, install band, device tabs and the live demo on test network E1. */
(function () {
  "use strict";
  var $ = function (id) { return document.getElementById(id); };
  var qa = function (sel, el) { return Array.prototype.slice.call((el || document).querySelectorAll(sel)); };
  var root = document.documentElement;
  function fmt(n) { return n === Infinity ? "∞" : Math.round(n).toLocaleString("en-US"); }
  function fmt2(n) { return (Math.round(n * 100) / 100).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
  function store(k, v) { try { if (v == null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) { /* storage blocked */ } }
  function load(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }

  /* ---------------------------------------------------------------- theme */
  var THEME_KEY = "ligtas.site.theme";
  var theme = load(THEME_KEY) || "auto";
  function applyTheme() {
    if (theme === "auto") root.removeAttribute("data-theme"); else root.setAttribute("data-theme", theme);
    var b = $("theme-btn"), name = { auto: "automatic", light: "light", dark: "dark" }[theme];
    b.setAttribute("aria-label", "Color theme: " + name + ". Change theme.");
    b.title = "Theme: " + name;
    b.querySelector("use").setAttribute("href", theme === "auto" ? "#i-auto" : theme === "dark" ? "#i-moon" : "#i-sun");
  }
  $("theme-btn").addEventListener("click", function () {
    theme = { auto: "light", light: "dark", dark: "auto" }[theme] || "auto";
    store(THEME_KEY, theme === "auto" ? null : theme);
    applyTheme();
    if (window.LigtasMap) renderDemo();
  });
  applyTheme();

  /* ---------------------------------------------------------------- install */
  var installStatus = $("install-status"), installPrompt = null;
  var ua = navigator.userAgent || "";
  var isIOS = /iPad|iPhone|iPod/.test(ua) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  var isAndroid = /Android/i.test(ua);
  var standalone = (window.matchMedia && window.matchMedia("(display-mode: standalone)").matches) || navigator.standalone === true;
  var embedded = false;
  try { embedded = window.self !== window.top; } catch (e) { embedded = true; }
  function say(msg) { if (installStatus) installStatus.textContent = msg; }
  function showDev(dev, focus) {
    qa(".dev-tabs [data-dev]").forEach(function (b) {
      var on = b.getAttribute("data-dev") === dev;
      b.setAttribute("aria-selected", on ? "true" : "false");
      b.tabIndex = on ? 0 : -1;
      $("dp-" + b.getAttribute("data-dev")).hidden = !on;
      if (on && focus) b.focus();
    });
  }
  qa(".dev-tabs [data-dev]").forEach(function (b, i, all) {
    b.addEventListener("click", function () { showDev(b.getAttribute("data-dev")); });
    b.addEventListener("keydown", function (e) {
      var j = e.key === "ArrowRight" ? (i + 1) % all.length : e.key === "ArrowLeft" ? (i - 1 + all.length) % all.length : -1;
      if (j < 0) return;
      e.preventDefault(); showDev(all[j].getAttribute("data-dev"), true);
    });
  });
  showDev(isIOS ? "ios" : isAndroid ? "android" : "desktop");
  if (standalone) say("LIGTA-S is installed and open as an app.");
  else if (location.protocol === "file:") say("This copy of the page was opened from a file. Install LIGTA-S from its website, or open the app file directly.");
  function noPromptText() {
    if (embedded) return "This copy of the page is shown inside another site, which blocks installing. Open the LIGTA-S website in Chrome, Edge or Safari to install it.";
    if (isIOS) return "On iPhone and iPad, install LIGTA-S from Safari: tap Share, then Add to Home Screen.";
    return "Install LIGTA-S from your browser's menu with the steps shown. If it is already installed, open it from your apps.";
  }
  document.addEventListener("click", function (e) {
    var trigger = e.target.closest ? e.target.closest("[data-install]") : null;
    if (!trigger) return;
    if (installPrompt) {
      e.preventDefault();
      var p = installPrompt;
      installPrompt = null;
      p.prompt();
      p.userChoice.then(function (c) {
        say(c && c.outcome === "accepted" ? "LIGTA-S is being installed. Look for it with your other apps." : "Install cancelled. You can install LIGTA-S from this page at any time.");
      }).catch(function () {});
      return;
    }
    if (trigger.tagName === "BUTTON") {
      say(noPromptText());
      var box = document.querySelector(".how-install");
      if (box && box.scrollIntoView) box.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  });
  window.addEventListener("beforeinstallprompt", function (e) {
    e.preventDefault();
    installPrompt = e;
    say("");
  });
  window.addEventListener("appinstalled", function () {
    installPrompt = null;
    say("LIGTA-S is installed. Open it from your home screen or app list.");
  });
  if ("serviceWorker" in navigator && window.isSecureContext && location.protocol !== "file:") {
    window.addEventListener("load", function () { navigator.serviceWorker.register("sw.js", { scope: "./" }).catch(function () {}); });
  }

  /* ---------------------------------------------------------------- demo */
  var E = window.LigtasEngine, M = window.LigtasMap;
  var data = JSON.parse($("ligtas-demo").textContent);
  var st = { scen: "AL3", rule: "lex", ch: "" };
  var cache = {};
  function scenSpec() {
    var sp = data.scenarios.filter(function (s) { return s.id === st.scen; })[0] || data.scenarios[0];
    var ch = data.channels.filter(function (c) { return c.id === st.ch; })[0];
    return { id: sp.id, name: sp.name, zones: sp.zones, closed: (sp.closed || []).concat(ch ? ch.bridges : []) };
  }
  function compute(rule) {
    var key = st.scen + "|" + st.ch + "|" + rule;
    if (!cache[key]) {
      var inst = E.makeInstance(data), sc = E.scenario(scenSpec());
      var p = rule === "near" ? E.nearest(inst, sc) : E.evaluate(inst, sc, rule);
      p.inst = inst; p.sc = sc; p.rule = rule;
      cache[key] = p;
    }
    return cache[key];
  }
  function flows(p) {
    var I = p.inst, out = [];
    if (p.rule === "near") {
      p.choice.forEach(function (c, a) {
        if (!c) return;
        out.push({ path: E.route(I, p.sc, I.origins[a].node, c.node).path, persons: c.persons, title: I.origins[a].id + ": " + fmt(c.persons) + " evacuees, " + c.minutes + " min" });
      });
      return out;
    }
    var pairs = {};
    p.x.forEach(function (r) {
      var s = p.slots[r.k].s, k = r.a + ">" + s;
      if (!pairs[k]) pairs[k] = { a: r.a, s: s, n: 0, room: 0 };
      pairs[k].n += r.f;
      if (p.slots[r.k].tier === 2) pairs[k].room += r.f;
    });
    Object.keys(pairs).forEach(function (k) {
      var q = pairs[k], o = I.origins[q.a], sh = I.shelters[q.s];
      out.push({ path: E.route(I, p.sc, o.node, sh.node).path, persons: q.n, tone: q.room === q.n ? "room" : "",
                 title: o.id + " to " + sh.id + ": " + fmt(q.n) + " evacuees, " + p.T[q.a][q.s] + " min" });
    });
    return out;
  }
  function notes(p) {
    var I = p.inst, out = {};
    if (p.rule === "near") {
      p.sites.forEach(function (s) { out[s.id] = s.overflow > 0 ? { text: fmt(s.load) + " sent, " + fmt(s.overflow) + " over", tone: "over" } : { text: fmt(s.load) + " sent" }; });
      return out;
    }
    var by = {};
    I.shelters.forEach(function (sh, s) {
      var id = I.nodes[sh.node];
      if (!by[id]) by[id] = { load: 0, rooms: 0 };
      by[id].load += p.load[s] || 0;
      by[id].rooms += p.roomsClosed[s] || 0;
    });
    Object.keys(by).forEach(function (id) {
      if (by[id].load > 0) out[id] = by[id].rooms ? { text: fmt(by[id].load) + " · " + by[id].rooms + " rooms", tone: "room" } : { text: fmt(by[id].load) };
    });
    return out;
  }
  function seg(el, cur, items, onPick) {
    if (items) el.innerHTML = items.map(function (it) { return '<button type="button" data-v="' + it[0] + '">' + it[1] + '</button>'; }).join("");
    qa("button", el).forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-v") === cur ? "true" : "false");
      b.onclick = function () { onPick(b.getAttribute("data-v")); };
    });
  }
  function kpi(v, label, tone) { return '<div class="kpi ' + (tone || "") + '"><b>' + v + '</b><span>' + label + '</span></div>'; }
  function renderDemo() {
    var sp = data.scenarios.filter(function (s) { return s.id === st.scen; })[0];
    var lockedCh = (sp.closed || []).length > 0;
    if (lockedCh) st.ch = "";
    seg($("d-scen"), st.scen, data.scenarios.map(function (s) { return [s.id, s.name]; }), function (v) { st.scen = v; renderDemo(); });
    seg($("d-rule"), st.rule, null, function (v) { st.rule = v; renderDemo(); });
    seg($("d-ch"), lockedCh ? "" : st.ch, null, function (v) { st.ch = v; renderDemo(); });
    qa("#d-ch button").forEach(function (b) { b.disabled = lockedCh; });
    var out = $("demo-out");
    out.classList.add("computing");
    setTimeout(function () {
      var p = compute(st.rule), lex = compute("lex"), time = compute("time"), spec = scenSpec();
      var h = '<div class="kpis">';
      if (p.rule === "near") {
        h += kpi(fmt(p.overflow), "evacuees arrive at shelters that are already full", p.overflow ? "bad" : "good");
        h += kpi(fmt2(p.meanTime) + "<small style=\"font-size:.5em\"> min</small>", "mean trip, ignoring capacity");
        h += kpi(fmt(p.sites.filter(function (s) { return s.overflow > 0; }).length), "shelter sites over capacity");
        h += kpi(fmt(p.moved), "evacuees sent");
      } else {
        h += kpi(fmt(p.roomsClosedTotal), "classrooms closed, packed 18 per room", p.roomsClosedTotal ? "bad" : "good");
        h += kpi(fmt(p.learnersDisplaced), "learners displaced", p.learnersDisplaced ? "bad" : "good");
        h += kpi(fmt2(p.meanTime) + '<small style="font-size:.5em"> min</small>', "mean trip");
        h += kpi(p.clearance === Infinity ? "∞" : fmt(p.clearance) + '<small style="font-size:.5em"> min</small>', "clearance time (lower bound " + fmt(p.clearanceLB) + ")", "good");
      }
      h += '</div>';
      if (p.rule !== "near") {
        var D = p.demand || 1, parts = [["t-ec", p.personsEc, "Non-school space"], ["t-open", p.personsOpen, "School open space"], ["t-room", p.personsRoom, "Classrooms"], ["t-none", p.unplaced, "Not placed"]];
        h += '<div class="tierbar" role="img" aria-label="' + parts.map(function (x) { return x[2] + " " + fmt(x[1]); }).join(", ") + '">' + parts.map(function (x) { return x[1] > 0 ? '<i class="' + x[0] + '" style="width:' + (100 * x[1] / D).toFixed(2) + '%"></i>' : ""; }).join("") + '</div>';
        h += '<div class="tierlegend">' + parts.map(function (x) { return '<span><i class="sw ' + x[0] + '"></i>' + x[2] + " " + fmt(x[1]) + '</span>'; }).join("") + '</div>';
      }
      var msg = "", warn = false;
      if (p.rule === "lex") {
        msg = "Of " + fmt(p.demand) + " evacuees (" + fmt(p.vulnerable) + " vulnerable), " + fmt(p.placed) + " are placed. ";
        if (time.roomsClosedTotal > p.roomsClosedTotal) msg += "A time-only plan would close " + fmt(time.roomsClosedTotal) + " classrooms; this plan closes " + fmt(p.roomsClosedTotal) + ", for " + fmt2(p.meanTime - time.meanTime) + " more minutes of mean travel.";
        else msg += "Here the time-only plan closes the same " + fmt(p.roomsClosedTotal) + " classrooms" + (nonRoomFull(p) ? ": every non-school and school open space is already in use, so the rest must go to classrooms." : ".") + " The shelters are " + Math.round(100 * p.placed / totalCap(p)) + "% full.";
        if (p.unplaced) { msg += " " + fmt(p.unplaced) + " residents are cut off from every shelter with room."; warn = true; }
      } else if (p.rule === "time") {
        msg = "The fastest plan closes " + fmt(p.roomsClosedTotal) + " classrooms. " + (lex.roomsClosedTotal < p.roomsClosedTotal ?
          "The school-preserving plan closes " + fmt(lex.roomsClosedTotal) + " (" + fmt(lex.learnersDisplaced) + " learners displaced instead of " + fmt(p.learnersDisplaced) + ")." :
          "Here the school-preserving plan closes the same number" + (nonRoomFull(lex) ? ": every non-school and school open space is already in use." : "."));
        warn = p.roomsClosedTotal > lex.roomsClosedTotal;
      } else {
        msg = "Everyone heads to the closest shelter site, whatever its capacity. " + (p.overflow ? fmt(p.overflow) + " evacuees find it full and must move again." : "No site overflows in this scenario.");
        warn = p.overflow > 0;
      }
      if (st.ch && p.rule !== "near") msg += " Channel " + st.ch + " cut: clearance " + (p.clearance === Infinity ? "has no finite time" : fmt(p.clearance) + " min") + ".";
      h += '<p class="demo-say' + (warn ? " warn" : "") + '">' + msg + '</p>';
      out.innerHTML = h;
      out.classList.remove("computing");
      M.draw($("demo-map"), data, { scenario: spec, flows: flows(p), siteNotes: notes(p), label: "Map of test network E1 (synthetic), " + spec.name + (st.ch ? ", channel " + st.ch + " cut" : "") + ". " + (p.rule === "near" ? "Nearest-site rule." : fmt(p.roomsClosedTotal) + " classrooms closed.") });
    }, 10);
  }
  function nonRoomFull(p) {
    var cap = 0;
    p.slots.forEach(function (s) { if (s.tier < 2) cap += s.cap; });
    return p.personsEc + p.personsOpen >= cap;
  }
  function totalCap(p) {
    var t = 0;
    p.slots.forEach(function (s) { t += s.cap; });
    return t || 1;
  }
  var resizeT = null;
  window.addEventListener("resize", function () { clearTimeout(resizeT); resizeT = setTimeout(renderDemo, 250); });
  renderDemo();
})();
